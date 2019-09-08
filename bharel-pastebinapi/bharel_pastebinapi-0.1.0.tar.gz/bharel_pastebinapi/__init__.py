from typing import (List, Optional, AsyncIterator,
                    cast, Iterable, TypeVar, no_type_check)
import operator
from itertools import takewhile
from dataclasses import dataclass
from functools import partial
from datetime import datetime
import dateutil.parser
import aiohttp
import asyncio
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from lxml.html import document_fromstring

__author__ = "Bar Harel"
__version__ = "0.1.0"

_PASTEBIN_URL = "https://pastebin.com/"
_PASTEBIN_RAW_URL = "https://pastebin.com/raw/"
_PASTEBIN_ARCHIVE_URL = urljoin(_PASTEBIN_URL, "archive")
_PASTEBIN_ROBOTS_URL = urljoin(_PASTEBIN_URL, "robots.txt")
_T = TypeVar("_T")


import locale  # noqa
_language_code, _encoding = locale.getlocale(locale.LC_TIME)
if _language_code != "en-US":
    # Trying to mess my datetime 'ey? Well I won't let you!
    try:
        locale.setlocale(locale.LC_TIME, ("en-US", "UTF-8"))
    except locale.Error:
        # Fine. You won.
        import warnings
        warnings.warn("Unable to check or set system locale. Date parsing "
                      "might be inaccurate.")
del locale, _language_code, _encoding


@dataclass
class Paste:
    id: str
    name: str
    author: str
    timestamp: datetime
    content: str

    @property
    def size(self):
        """Paste's size"""
        return len(self.content)


class PastebinAPI:
    """An API for pastebin

    We do not use the pastebin API, but are implementing an internal
    crawler instead. Pastebin API, developer key, and scrapper support
    might be added in the future.

    Attributes:
        user_agent: User agent to send the requests as.
        respect_robots: Boolean stating whether we should respect robots.txt
        or not. Defaults to true.
    """
    user_agent: Optional[str]
    respect_robots: bool

    def __init__(self, *, respect_robots: bool = True) -> None:
        """Initialize the Pastebin API

        Args:
            respect_robots: Should we respect robots.txt? Defaults to True.
        """
        self._robot_parser: Optional[RobotFileParser] = None
        self._user_agent = None
        self._session = None
        self._connected = False

        self.respect_robots = respect_robots

    async def __aenter__(self):
        """For use as a context manager"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """For use as a context manager"""
        await self.close()

    async def connect(self):
        """Connect to Pastebin"""
        user_agent = self.user_agent
        if user_agent:
            self._session = aiohttp.ClientSession(
                headers=("User-Agent", user_agent))
        else:
            self._session = aiohttp.ClientSession()

        if self.respect_robots:
            await self._parse_robots()

        self._connected = True

    async def close(self):
        """Close the API session"""
        session = self._session
        if session:
            self._session = None
            self._connected = False
            await session.close()

    async def upload_paste(self, paste: Paste):
        """Uploads a Pastebin paste.

        Will be implemented in the future.
        """
        pass

    async def get_latest_pastes(self) -> List[Paste]:
        """Gets the latest pastes over from Pastebin's archive.

        The pastes are received in the order they are found on the pastebin
        archive: Top to bottom, newest to oldest. Contrary to it's name, the
        archive sources the latest pastes from pastebin.

        Returns:
            A list of pastes, newest to oldest.
        """
        pastes = [paste async for paste in self.iter_lastest_pastes()]
        pastes.sort(key=operator.attrgetter("timestamp"), reverse=True)
        return pastes

    @no_type_check
    async def get_paste(self, paste_id: str) -> Paste:
        """Fetches a paste from the server.

        Args:
            paste_id: ID of the paste on pastebin.

        Returns:
            Parsed Paste object.
        """
        data = await self._fetch(urljoin(_PASTEBIN_URL, paste_id))
        tree = document_fromstring(data)

        def validate_element(element: Optional[_T], name: str) -> _T:
            if element is None:
                raise RuntimeError(f"Unknown response returned, "
                                   f"{name} not found.")
            return element

        info_element = validate_element(
            tree.find(".//div[@class='paste_box_info']"),
            "paste info")

        name_element = validate_element(info_element.find(".//h1"),
                                        "paste name")

        paste_name = (name_element.text or "").strip()

        user_image_element = validate_element(info_element.find(".//img"),
                                              "user image")

        paste_author = (user_image_element.tail or "").strip()

        date_element = validate_element(info_element.find(".//span"),
                                        "paste date")

        raw_paste_date = validate_element(date_element.get("title"),
                                          "paste date title")

        # Let's hope the user's locale won't cause an issue on this one.
        # Why Pastebin couldn't use UTC?
        paste_date = dateutil.parser.parse(raw_paste_date,
                                           tzinfos={"CDT": -18000})

        try:
            paste_content = await self._fetch(urljoin(_PASTEBIN_RAW_URL,
                                                      paste_id))

        # If it isn't allowed according to robots.txt, parse from html.
        except ConnectionRefusedError:
            content_element = validate_element(
                tree.find(".//ol"),
                "paste content")
            paste_content = content_element.text_content()

        return Paste(author=paste_author, name=paste_name, id=paste_id,
                     content=paste_content, timestamp=paste_date)

    async def iter_lastest_pastes(
            self, *, later_than: str = None) -> AsyncIterator[Paste]:
        """Iterates over Pastebin's archive.

        The pastes are received in an UNDEFINED order, first come first serve.
        Contrary to it's name, the archive sources the latest pastes
        from pastebin.

        Note: Using this function repeatedly does not guarantee we'll see all
        pastes. Pastebin's API has a rate limiter. Gaps can form in the data,
        even with constant fetches. We'll return as many pastes as we can get
        before the rate limit applies.

        Args:
            later_than: An optional Paste ID. Do not return pastes created
            before the given paste. We do not guarantee to return all pastes
            before that paste. If we do reach that paste in chronological
            order, we'll stop.

        Returns:
            An async iterator over pastes, from newest to oldest.
        """
        paste_ids: Iterable[str] = await self._get_lastest_paste_ids()

        if later_than:
            paste_ids = takewhile(later_than.__ne__, paste_ids)

        paste_futures = map(self.get_paste, paste_ids)

        for future in asyncio.as_completed(paste_futures):  # type: ignore
            yield await future

    async def _get_lastest_paste_ids(self) -> List[str]:
        """Fetch and parse the latest paste ids from the Pastebin Archive.

        Returns:
            List of Pastebin IDs.
        """
        data = await self._fetch(_PASTEBIN_ARCHIVE_URL)
        tree = document_fromstring(data)
        table = tree.find(".//table[@class='maintable']/tbody")

        # Pastebin are stupid. They're blocking us from the
        # archive page if we scrape too fast, but the public pastes
        # menu on the side still works and is fully updated >.<
        if table is None:
            public_table = tree.find(".//ul[@class='right_menu']")
            if public_table is None:
                raise RuntimeError("Unknown response returned.")
            link_elements = public_table.iterfind(".//a")

        else:
            link_elements = table.iterfind(".//a/preceding-sibling::img")

        paste_ids = []

        # Retrieve paste ID from paste's url.
        for element in link_elements:
            url_path = element.get("href")
            if not url_path:
                raise RuntimeError("Invalid 'a' tag acquired.")
            paste_ids.append(url_path.lstrip("/"))

        return paste_ids

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value):
        old_ua = self._user_agent
        self._user_agent = value

        # User agent was changed, reconnect
        if value != old_ua and self._session:
            asyncio.ensure_future(self.connect)

    async def _fetch(self, url: str) -> str:
        """Requests a resource from the given URL.

        Checks for robots.txt on the way.

        Args:
            url: URL as a string

        Returns:
            aiohttp.ClientResponse with the server's response.

        Raises:
            ConnectionRefusedError: Robots.txt disallows entering that
            url.
            IOError: Client is not connected.
        """
        if not self._connected:
            raise IOError("Client is not connected. Please call connect() "
                          "method first.")
        if self.respect_robots:
            if not self._can_fetch(url):  # type: ignore
                raise ConnectionRefusedError(
                    "Disallowed by robots.txt. Attempted URL - " + url)
            # TODO: Abide by request_rate and crawl_delay.

        assert self._session

        async with self._session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def _parse_robots(self) -> None:
        """Parses robots.txt

        As a side-effect, caches some data according to our user
        agent for a cleaner API.
        """
        if not self._session:
            return

        parser = self._robot_parser
        if parser is None:
            parser = self._robot_parser = RobotFileParser(_PASTEBIN_ROBOTS_URL)
            async with self._session.get(_PASTEBIN_ROBOTS_URL) as resp:
                resp.raise_for_status()
                robot_lines = (await resp.text()).splitlines()
            parser.parse(robot_lines)

        agent = self.user_agent or "*"
        self._can_fetch = partial(parser.can_fetch, agent)
        self._crawl_delay = parser.crawl_delay(agent)
        self._request_rate = parser.request_rate(agent)

    @property
    def respect_robots(self):
        return self._respect_robots

    @respect_robots.setter
    def respect_robots(self, value):
        """Setup robot parser if value is True"""
        if value and self._session:
            asyncio.ensure_future(self._parse_robots)
        self._respect_robots = value
