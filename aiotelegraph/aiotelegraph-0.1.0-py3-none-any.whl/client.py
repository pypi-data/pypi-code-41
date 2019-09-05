from .entities import Account, Node, Page
from .exceptions import TelegraphRequestException, TelegraphTokenException
import aiohttp
from typing import Iterable


def token_required(coroutine):
    async def wrapper(self, *args, **kwargs):
        if self.access_token is None:
            raise TelegraphTokenException()
        return coroutine(self, *args, **kwargs)
    return wrapper


class TelegraphClient:
    BASE_URL = "https://api.telegra.ph/{method}"
    PATH_URL = "https://api.telegra.ph/{method}/{path}"

    def __init__(self, access_token: (str, None)=None, auth_url: (str, None)=None):
        self.access_token = access_token
        self.auth_url = auth_url

    async def request(self, method: str, path: (str, None)=None, **params):
        if path is None:
            url = self.BASE_URL.format(method=method)
        else:
            url = self.PATH_URL.format(method=method, path=path)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params) as response:
                result = await response.json()
                if result["ok"]:
                    return result["result"]
                else:
                    raise TelegraphRequestException(error=result["error"], method=method, **params)

    async def create_account(self, short_name: str, author_name: (str, None)=None,
                             author_url: (str, None)=None):
        params = {}
        if author_name is not None:
            params["author_name"] = author_name
        if author_url is not None:
            params["author_url"] = author_url
        data = await self.request(method="createAccount", short_name=short_name, **params)
        self.access_token = data["access_token"]
        self.auth_url = data["auth_url"]
        return Account.parse(data)

    @token_required
    async def edit_account_info(self, short_name: (str, None)=None, author_name: (str, None)=None,
                                author_url: (str, None)=None):
        params = {}
        if short_name is not None:
            params["short_name"] = short_name
        if author_name is not None:
            params["author_name"] = author_name
        if author_url is not None:
            params["author_url"] = author_url
        data = await self.request(method="editAccountInfo", access_token=self.access_token,
                                  **params)
        return Account.parse(data)

    @token_required
    async def get_account_info(self, *fields):
        data = await self.request(method="getAccountInfo", access_token=self.access_token,
                                  fields=list(fields))
        return Account.parse(data)

    @token_required
    async def revoke_access_token(self):
        data = await self.request(method="revokeAccessToken", access_token=self.access_token)
        self.access_token = data["access_token"]
        self.auth_url = data["auth_url"]
        return Account.parse(data)

    @token_required
    async def create_page(self, title: str, content: Iterable[Node], author_name: (str, None)=None,
                          return_content: bool=False):
        params = {}
        if author_name is not None:
            params["author_name"] = author_name
        content = [c.render() for c in content]
        data = await self.request(method="createPage", access_token=self.access_token, title=title,
                                  content=content, return_content=return_content, **params)
        return Page.parse(data)

    @token_required
    async def edit_page(self, path: str, title: str, content: Iterable[Node],
                        author_name: (str, None)=None, author_url: (str, None)=None,
                        return_content: bool=False):
        params = {}
        if author_name is None:
            params["author_name"] = author_name
        if author_url is None:
            params["author_url"] = author_url
        content = [c.render() for c in content]
        data = await self.request(method="editPage", access_token=self.access_token, title=title,
                                  content=content, return_content=return_content, **params)
        return Page.parse(data)

    async def get_page(self, path: str, return_content: bool=False):
        data = await self.request(method="getPage", path=path, return_content=return_content)
        return Page.parse(data)

    @token_required
    async def get_page_list(self, offset: int=0, limit: int=50):
        data = await self.request(method="getPageList", access_token=self.access_token,
                                  offset=offset, limit=limit)
        pages = [Page.parse(page) for page in data["pages"]]
        return {"total_count": data["total_count"], "pages": pages}

    async def get_views(self, path: str, year: (int, None)=None, month: (int, None)=None,
                        day: (int, None)=None, hour: (int, None)=None):
        params = {}
        if year is not None:
            params["year"] = year
        if month is not None:
            params["month"] = month
        if day is not None:
            params["day"] = day
        if hour is not None:
            params["hour"] = hour
        data = await self.request(method="getViews", path=path, **params)
        return data["views"]

