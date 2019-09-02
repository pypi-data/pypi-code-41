"""
    Returns the current user object as json
"""
import tornado.web
from bluemax.utils import json_utils
from .user_mixin import UserMixin


class ProfileHandler(UserMixin, tornado.web.RequestHandler):  # pylint: disable=W0223
    """ this assumes the user is logged in """

    @tornado.web.authenticated
    async def get(self):
        """ return a json view of the current user """
        user = self.current_user
        self.set_header("content-type", "application/json")
        self.write(json_utils.dumps(user, indent=4))
