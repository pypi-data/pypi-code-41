import aiohttp
from base_client_library.factories.base import BaseFactory as SyncBaseFactory

class BaseFactory(SyncBaseFactory):

    async def api_get_request(self, **kwargs):

        path = kwargs.get("path", self.path)
        params = kwargs.get("params", {})

        url = f"{self.base_url}{path}"

        if not self.session:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=self.verify_ssl, params=params) as response:
                    return await response.json()

        async with self.session.get(url, ssl=self.verify_ssl, params=params) as response:
            return await response.json()
