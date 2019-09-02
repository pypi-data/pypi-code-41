"""
    Support for Tornado Authentication.
"""
from tornado.web import RequestHandler
from .user_mixin import UserMixin


class LogoutHandler(UserMixin, RequestHandler):  # pylint: disable=W0223
    """ We need to logout """

    def get(self):
        """ removes cookie and redirects to optional next argument """
        self.set_current_user(None)
        self.redirect(self.get_argument("next", "/"))
