"""
    Handle trakt.tv interactions
    This is a PARTIAL implementation of the API.
    Pull requests with more methods are welcome.
"""
from contextlib import suppress
import json
import os
from .aiohttp_device import aiohttp_trakt_device

CONF_PATH = os.path.expanduser('~/.trakt.conf')


class Trakt:
    """
        Handle Trakt's authentication using aiohttp_trakt_auth
        and expose an almost-complete Trakt API
    """

    def __init__(self, cid, csecret):
        self.cid = cid
        self.csecret = csecret
        self._cfg = False
        self.auth_data = False
        self._device = False

    @property
    def device(self):
        """ Device auth """
        if not self._device:
            self._device = aiohttp_trakt_device(self.cid, self.csecret)
        return self._device

    @property
    def cfg(self):
        """
            Read config from CONF_PATH as json
        """
        if not self._cfg:
            with suppress(OSError):
                self._cfg = json.load(open(CONF_PATH))
            self._cfg = {}
        return self._cfg

    @property
    async def clientsession(self):
        """ Get a client session authenticated for this device if not
            already on it """
        self.auth_data, session = await self.device.clientsession(
            self.cfg.get('trakt', {}))
        self.cfg['trakt'] = self.auth_data
        json.dump(self.cfg, open(CONF_PATH, 'w'))
        return session

    async def _url(self, url, method="get", data=False):
        """ Return a url, authenticated """
        with await self.clientsession as ses:
            method = getattr(ses, method)
            async with method(url.format(self.device.api_url),
                              data=data) as resp:
                assert resp.status == 200
                return resp.json()

    async def watchlist(self):
        """ Return show watchlist """
        return await self._url("{}/sync/watchlist/shows")

    async def calendars_shows(self, whom, name, date, number):
        """
            http://docs.trakt.apiary.io/
            #reference/calendars/my-shows/get-shows
        """
        assert whom in ["my", "all"]
        assert name in [False, "new", "premieres"]
        if not name:
            return await self._url(
                "{{}}/calendars/{}/shows/{}/{}".format(whom, date, number))
        else:
            return self._url(
                "{{}}/calendars/{}/shows/{}/{}/{}".format(
                    whom, name, date, number))

    async def calendars_movies(self, wich, date, number):
        """
            http://docs.trakt.apiary.io
            /#reference/calendars/my-movies/get-season-premieres
        """
        return await self._url(
            "{{}}/calendars/{}/movies/{}/{}".format(wich, date, number))

    async def checkin(self, episode=False, movie=False, foursquare=False,
                      **kwargs):
        """ Checkin on a movie or episode """
        if episode:
            data = {"episode": episode}
        elif movie:
            data = {"movie": movie}
        else:
            raise Exception("You need to specify either a movie or an episode")
        data.update(kwargs)

        if foursquare:
            data.update(foursquare)

        return await self._url("{}/checkin", "post", data)

    async def genres(self, type_):
        """ Genres """
        assert type_ in ["movies", "shows"]
        return await self._url("{{}}/genres/{}".format(type_))

    async def _sorted(self, type_, sorting, period=False):
        """
            Return any movie or show sorting, as in:

            http://docs.trakt.apiary.io/#reference/movies
            and
            http://docs.trakt.apiary.io/#reference/shows/

            for played, watched, collected, trending, popular, anticipated

            for movies we also have boxoffice
        """
        assert period in [False, "weekly", "monthly", "yearly", "all"]

        with_period = ["played", "watched", "collected"]
        without_period = ["trending", "popular", "anticipated", "boxoffice"]

        if sorting in with_period:
            assert period
            return self._url("{{}}/{}/{}/{}".format(
                type_, sorting, period))
        elif sorting in without_period:
            if sorting == "boxoffice":
                assert type_ == "movies"
            return self._url("{{}}/{}/{}".format(type_, sorting))
        else:
            raise Exception("Invalid sorting type")

    async def movies(self, sorting, period=False):
        """ see ``self._sorted`` """
        return await self._sorted("movies", sorting, period)

    async def shows(self, sorting, period=False):
        """ see ``self._sorted`` """
        return await self._sorted("shows", sorting, period)

    async def translations(self, type_, trakt_id_or_slug, lang):
        """
            Returns translations for a movie or show, by id_or_slug for lang
        """
        assert type_ in ["movies", "shows"]
        assert len(lang) == 2
        return await self._url("{{}}/{}/{}/translations/{}".format(
            type_, trakt_id_or_slug, lang))

    async def seasons(self, trakt_id_or_slug, season=''):
        """
            Return all seasons with episode number
            IF season number is specified, it'll return all episode
            info for that season
        """
        if season:
            season = "/{}".format(season)
        return await self._url("{{}}/shows/{}/seasons{}".format(
            trakt_id_or_slug, season))

    async def episode(self, trakt_id_or_slug, season, episode):
        """ Return single info for an episode. """
        return await self._url("{{}}/shows/{}/seasons/{}/episodes/{}".format(
            trakt_id_or_slug, season, episode))
