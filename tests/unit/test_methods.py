import pytest


def test_has_trakt():
    try:
        from trakt_aiohttp import Trakt
    except ImportError:
        assert False


def test_has_shows():
    from trakt_aiohttp import Trakt
    assert Trakt.shows


def test_has_movies():
    from trakt_aiohttp import Trakt
    assert Trakt.movies


@pytest.mark.asyncio
async def test_trakt_get_movies():
    import trakt_aiohttp
    periods = ["weekly", "monthly", "yearly", "all"]
    with_period = ["played", "watched", "collected"]
    without_period = ["trending", "popular", "anticipated", "boxoffice"]
    trakt = trakt_aiohttp.Trakt(
        "9b36d8c0db59eff5038aea7a417d73e69aea75b41aac771816d2ef1b3109cc2f",
        "fake")
    trakt.device.api_url = ("https://private-anon-16f878"
                            "fdf-trakt.apiary-mock.com")

    for method in with_period:
        for period in periods:
            try:
                await trakt.movies(method, period)
            except Exception as err:
                print(err)
                assert False, "Errored: {}".format(method)

    for method in without_period:
        try:
            trakt.movies(method)
        except Exception as err:
            print(err)
            assert False, "Errored: {}".format(method)
