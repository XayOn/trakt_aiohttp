"""
    Handle aiohttp berarer authentication for devices
"""

import aiohttp
import asyncio
from contextlib import suppress


class aiohttp_trakt_device:
    """
        To auth a device, call trakt_auth_device with a callback
        that'll print verification_url and user_code from the args' receive
        dict

        ::

            def callback(args):
                print(args['verification_url'])
                print(args['user_code'])

        Trakt's device authentication requires the user to login into
        verification_url with their credentials, and enter user_code.
        With that, we automatically handle authentication polling
        until we get the authorization token.

        I don't offer configuration management in this library, wich means
        it'll always ask the user for a new authorization, wich is not
        ideal, you must implement your own config management and save
        the token for later use.

    """
    def __init__(self, cid, csecret):
        self.api_url = 'https://api-v2launch.trakt.tv'
        self.cid = cid
        self.csecret = csecret

    @property
    def device_url(self):
        """ device url """
        return "{}/oauth/device".format(self.api_url)

    @property
    def token_url(self):
        return "{}/token".format(self.device_url)

    @property
    def code_url(self):
        return "{}/code".format(self.device_url)

    async def trakt_auth_device(self, advise_callback):
        """
            returns the full authorization data,
            as a dict, from wich we'll get "access_token"
        """
        with aiohttp.ClientSession() as session:
            async with session.post(
                self.code_url, data={"client_id": self.cid}
            ) as resp:
                assert resp.status == 200
                auth_data = await resp.json()

        await advise_callback(auth_data)

        with suppress(TimeoutError):
            data = {"client_id": self.cid, "client_secret": self.csecret,
                    "code": auth_data['device_code']}
            with asyncio.timeout(auth_data['expires_in']):
                with aiohttp.ClientSession() as session:
                    while True:
                        async with session.post(self.token_url, data=data) as resp:
                            if resp.status == 200:
                                return await resp.json()
                            else:
                                await asyncio.sleep(auth_data["interval"])
        return False

    async def clientsession(self, auth_data=False, adv=False):
        """
            If you're doing a simple CLI version, you can use the
            ``self.clientsession`` method, wich prints the auth data to the
            user, and returns the auth_data + an auth clientsession, and, if
            no token has been passed to it as an argument, it'll get a new one
        """

        async def default_adv(auth):
            """ Basic verification message """
            print("Go to {verification_url} and enter {user_code}".format(
                **auth))

        if not adv:
            adv = default_adv

        if not auth_data:
            auth_data = await self.trakt_auth_device(adv)

        bearer = "Bearer {}".format(auth_data['access_token'])
        return auth_data, aiohttp.ClientSession(headers={
            "Authorization": bearer, 'trakt_api_version': "2",
            'trakt_api_key': self.cid})
