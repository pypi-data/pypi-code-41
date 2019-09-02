"""
    Support for Tornado Authentication.
"""
import logging
from bluemax.utils import json_utils

LOGGER = logging.getLogger(__name__)


class UserMixin:
    """
        Should be mixed in with WebsocketHandlers
        or RequestHandlers. Make sure it is the
        first class in the declaration as it
        overrides methods in both handlers.
    """

    @property
    def cookie_name(self):
        """ return the cookie_name declared in options"""
        return self.settings.get("cookie_name")

    def get_current_user(self):
        """ return the current user from the cookie """
        result = self.get_secure_cookie(self.cookie_name)
        LOGGER.debug("%s:%s", self.cookie_name, result)
        if result:
            result = json_utils.loads(result.decode("utf-8"))
        return result

    def set_current_user(self, value):
        """ put the current user in the cookie """
        if value:
            self.current_user = value
            self.set_secure_cookie(self.cookie_name, json_utils.dumps(value))
        else:
            self.clear_cookie(self.cookie_name)
