"""
    Support for Tornado Authentication.
"""
import asyncio
from tornado.web import RequestHandler, HTTPError
from .user_mixin import UserMixin


class LoginHandler(UserMixin, RequestHandler):  # pylint: disable=W0223
    """
        Can be called as ajax from the
        websocket client to get the auth cookie
        into the headers.
    """

    async def post(self):
        """ handle login post """
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        if username is None or password is None:
            raise HTTPError(403, "username or password is None")

        user = self.login(username, password)  # pylint: disable=E1101
        if asyncio.iscoroutine(user):
            user = await user
        if user:
            self.set_current_user(user)
            self.redirect(self.get_argument("next", "/"))
        else:
            self.set_status(403)
            self.finish("<html><body>Username or password incorrect</body></html>")
