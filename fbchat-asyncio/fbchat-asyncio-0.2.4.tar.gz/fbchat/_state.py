# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import attr
import bs4
import re
import random
import asyncio
from yarl import URL
from aiohttp import ClientSession

from . import _util, _exception

FB_DTSG_REGEX = re.compile(r'name="fb_dtsg" value="(.*?)"')


def find_input_fields(html):
    return bs4.BeautifulSoup(html, "html.parser", parse_only=bs4.SoupStrainer("input"))


def is_home(url):
    path = URL(url).path
    # Check the urls `/home.php` and `/`
    return "home" in path or "/" == path


async def _2fa_helper(session, code, resp, log):
    soup = find_input_fields(await resp.text())
    data = dict()

    url = "https://m.facebook.com/login/checkpoint/"

    data["approvals_code"] = code
    data["fb_dtsg"] = soup.find("input", {"name": "fb_dtsg"})["value"]
    data["nh"] = soup.find("input", {"name": "nh"})["value"]
    data["submit[Submit Code]"] = "Submit Code"
    data["codes_submitted"] = 0
    log.info("Submitting 2FA code.")

    resp = await session.post(url, data=data)

    if is_home(resp.url):
        return resp

    del data["approvals_code"]
    del data["submit[Submit Code]"]
    del data["codes_submitted"]

    data["name_action_selected"] = "save_device"
    data["submit[Continue]"] = "Continue"
    log.info("Saving browser.")
    # At this stage, we have dtsg, nh, name_action_selected, submit[Continue]
    resp = await session.post(url, data=data)

    if is_home(resp.url):
        return resp

    del data["name_action_selected"]
    log.info("Starting Facebook checkup flow.")
    # At this stage, we have dtsg, nh, submit[Continue]
    resp = await session.post(url, data=data)

    if is_home(resp.url):
        return resp

    del data["submit[Continue]"]
    data["submit[This was me]"] = "This Was Me"
    log.info("Verifying login attempt.")
    # At this stage, we have dtsg, nh, submit[This was me]
    resp = await session.post(url, data=data)

    if is_home(resp.url):
        return resp

    del data["submit[This was me]"]
    data["submit[Continue]"] = "Continue"
    data["name_action_selected"] = "save_device"
    log.info("Saving device again.")
    # At this stage, we have dtsg, nh, submit[Continue], name_action_selected
    resp = await session.post(url, data=data)
    return resp


@attr.s(slots=True)  # TODO i Python 3: Add kw_only=True
class State(object):
    """Stores and manages state required for most Facebook requests."""

    fb_dtsg = attr.ib()
    _revision = attr.ib()
    _session = attr.ib()
    _counter = attr.ib(default=0)
    _logout_h = attr.ib(default=None)

    def get_user_id(self):
        rtn = self.get_cookies().get("c_user")
        if rtn is None:
            return None
        return rtn.value

    def get_params(self):
        self._counter += 1  # TODO: Make this operation atomic / thread-safe
        return {
            "__a": 1,
            "__req": _util.str_base(self._counter, 36),
            "__rev": self._revision,
            "fb_dtsg": self.fb_dtsg,
        }

    @classmethod
    async def login(cls, email, password, on_2fa_callback, user_agent=None, loop=None, log=None):
        session = ClientSession(loop=loop or asyncio.get_event_loop(), headers={
            "User-Agent": user_agent or random.choice(_util.USER_AGENTS),
            "Referer": "https://www.facebook.com"
        })

        resp = await session.get("https://m.facebook.com/")
        soup = find_input_fields(await resp.text())
        data = dict(
            (elem["name"], elem["value"])
            for elem in soup
            if elem.has_attr("value") and elem.has_attr("name")
        )
        data["email"] = email
        data["pass"] = password
        data["login"] = "Log In"

        resp = await session.post("https://m.facebook.com/login.php?login_attempt=1", data=data)
        text = await resp.text()

        # Usually, 'Checkpoint' will refer to 2FA
        if "checkpoint" in resp.url.path and ('id="approvals_code"' in text.lower()):
            code = await on_2fa_callback()
            resp = await _2fa_helper(session, code, resp, log)

        # Sometimes Facebook tries to show the user a "Save Device" dialog
        if "save-device" in resp.url.path:
            resp = await session.get("https://m.facebook.com/login/save-device/cancel/")

        if is_home(resp.url):
            return await cls.from_session(session=session)
        else:
            raise _exception.FBchatUserError(
                "Login failed. Check email/password. "
                "(Failed on url: {})".format(str(resp.url))
            )

    async def is_logged_in(self):
        # Send a request to the login url, to see if we're directed to the home page
        url = "https://m.facebook.com/login.php?login_attempt=1"
        r = await self._session.get(url, allow_redirects=False)
        return "Location" in r.headers and is_home(r.headers["Location"])

    async def logout(self):
        logout_h = self._logout_h
        if not logout_h:
            url = _util.prefix_url("/bluebar/modern_settings_menu/")
            h_r = await self._session.post(url, data={"pmid": "4"})
            logout_h = re.search(r'name=\\"h\\" value=\\"(.*?)\\"', h_r.text).group(1)

        url = _util.prefix_url("/logout.php")
        resp = await self._session.get(url, params={"ref": "mb", "h": logout_h})
        return resp.status == 200

    @classmethod
    async def from_session(cls, session):
        resp = await session.get(_util.prefix_url("/"))

        text = await resp.text()

        soup = find_input_fields(text)

        fb_dtsg_element = soup.find("input", {"name": "fb_dtsg"})
        if fb_dtsg_element:
            fb_dtsg = fb_dtsg_element["value"]
        else:
            # Fall back to searching with a regex
            match = FB_DTSG_REGEX.search(text)
            if not match:
                raise _exception.FBchatUserError("Restoring session failed "
                                                 f"(response path: {resp.url.path})")
            fb_dtsg = match.group(1)

        revision = int(text.split('"client_revision":', 1)[1].split(",", 1)[0])

        logout_h_element = soup.find("input", {"name": "h"})
        logout_h = logout_h_element["value"] if logout_h_element else None

        return cls(
            fb_dtsg=fb_dtsg, revision=revision, session=session, logout_h=logout_h
        )

    def get_cookies(self):
        try:
            return self._session.cookie_jar._cookies["facebook.com"]
        except (AttributeError, KeyError):
            return None

    @classmethod
    async def from_cookies(cls, cookies, user_agent=None, loop: asyncio.AbstractEventLoop = None):
        session = ClientSession(loop=loop or asyncio.get_event_loop(), headers={
            "User-Agent": user_agent or random.choice(_util.USER_AGENTS),
            "Referer": "https://www.facebook.com"
        })
        session.cookie_jar._cookies["facebook.com"] = cookies
        return await cls.from_session(session=session)
