"""
Custom defined throttle classes.

Here are two throttling classes defined that should provide protection
against brute-force attacks. This is critical because truncated OTPs
like TOTP tokens are easy to brute force.
"""

__all__ = (
    "SimpleDelayingThrottle",
    "AbstractDelayingThrottle",
    "RecursiveDelayingThrottle",
)

import re
import abc
import time
import urllib.parse


from django.core.cache import cache as default_cache
from django.core.exceptions import ImproperlyConfigured

from rest_framework.throttling import BaseThrottle


from rest_multi_factor.settings import multi_factor_settings


class AbstractDelayingThrottle(BaseThrottle, metaclass=abc.ABCMeta):
    """Mixin class for brute-force protecting throttles."""

    @property
    @abc.abstractmethod
    def scope(self):
        """
        The scope name of the throttle class.

        :return: a scope name
        :type: str
        """

    @property
    @abc.abstractmethod
    def cache(self):
        """
        The cache backend to use.

        :return: the cache backend
        :rtype: django.core.cache.backends.base.BaseCache
        """

    @abc.abstractmethod
    def allow_request(self, request, view):
        """
        Tell whether the current request should be allowed or not.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The currently requested view
        :type view: rest_framework.views.APIView

        :return: Whether to allow the request or not
        :rtype: bool
        """

    @abc.abstractmethod
    def wait(self):
        """
        Get the wait period in seconds.

        Checks whether there should be a timeout or not
        before the next request, and how long in seconds.

        :return: The time to wait until the next request
        :rtype: int
        """

    def parse_timeout(self, value):
        """
        Parse a timeout specification.

        This is a string that begins with a value and ends
        with a timespan.

        The timespan must be either s (seconds), m (minutes),
        h (hours), d (days). the value must be a positive decimal.

        :return: The timeout in seconds.
        :rtype: int
        """
        if hasattr(self, "_parsed_timeout"):
            return getattr(self, "_parsed_timeout")

        pattern = re.compile(r"^(\d+)([smhd])$", flags=re.IGNORECASE)
        match = pattern.match(value)

        if match is not None:
            index = match.group(2).lower()
            value = int(match.group(1)) * {
                "s": 1, "m": 60, "h": 3600, "d": 86400
            }[index]

            setattr(self, "_parsed_timeout", value)

            return value

        raise ImproperlyConfigured(
            "The value of 'VERIFICATION_THROTTLE_TIMEOUT'"
            " must be in the format <value>[smhd] like for example ''30s'"
        )

    def get_tryouts(self):
        """
        Retrieve the number of tryouts to use.

        :return: The number of tryouts
        :rtype: int
        """
        return multi_factor_settings.VERIFICATION_THROTTLE_TRYOUTS

    def get_timeout(self):
        """
        Retrieve the time in seconds to use as timeout.

        :return: The timout in seconds
        :rtype: int
        """
        return self.parse_timeout(
            multi_factor_settings.VERIFICATION_THROTTLE_TIMEOUT
        )

    @classmethod
    def get_ident(cls, request):
        """
        Get the unique cache key for every token.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :return: The unique cache key
        :rtype: str
        """
        if not request.user.is_authenticated:
            raise ImproperlyConfigured(
                "Authentication must be checked before auth throttle"
            )

        if not request.auth:
            raise ImproperlyConfigured(
                "Authentication must be token based to use this throttle"
            )

        return urllib.parse.quote("{0} {1}".format(cls.scope, request.auth))

    @classmethod
    def clear(cls, request):
        """
        Clear the cache for a certain token.

        :param request: The current request instance
        :type request: rest_-framework.request.Request
        """
        instance = cls()
        instance.cache.delete(instance.get_ident(request))


class SimpleDelayingThrottle(AbstractDelayingThrottle):
    """
    Simple Delaying Throttle.

    This will force a timeout after a maximum number of
    allowed requests.
    """

    scope = "auth"
    timer = time.time
    cache = default_cache

    history = None
    timeout = None
    tryouts = None

    def allow_request(self, request, view):
        """
        Check whether or not to allow a request to verify.

        :param request: The current request instance.
        :type request: rest_framework.request.Request

        :param view: The view that is currently being accessed
        :type view: rest_framework.views.APIView

        :return: Whether the request should be further processed or not
        :rtype: bool
        """
        identifier = self.get_ident(request)
        expiration = self.get_cache_timeout()

        self.tryouts = self.get_tryouts()
        self.timeout = self.get_timeout()

        self.history = self.cache.get_or_set(identifier, (), expiration)

        wait_period = self.wait()
        if wait_period is not None and wait_period > 0:
            return False

        if wait_period is not None and wait_period <= 0:
            self.history = ()

        self.cache.set(identifier, (*self.history, self.timer()), expiration)
        return True

    def wait(self):
        """
        Calculate the number of seconds to wait until the next request.

        :return: The number of seconds to wait
        :rtype: None | int
        """
        if len(self.history) < self.tryouts:
            return None

        return (self.history[-1] + self.timeout) - self.timer()

    def get_cache_timeout(self):
        """
        Retrieve the expiration time of the cache.

        For Simple Delaying Throttle this is a constant of 1 hour.

        :return: The cache timeout
        :rtype: int
        """
        return 3600


class RecursiveDelayingThrottle(AbstractDelayingThrottle):
    """
    Recursive Delaying Throttle.

    Will add a required timeout between every request.
    This timeout will 'grow' after every request.

    The timeout will be calculated as <number of requests> multiplied
    by <specified time in settings>. and will have a roof that is
    specified by the maximum tryouts in the settings/
    """

    scope = 'delayed'
    cache = default_cache
    timer = time.time

    tryouts = None
    timeout = None

    def allow_request(self, request, view):
        """
        Check whether the request is allowed or not.

        The timeout between the requests is the timeout
        setting multiplied by the number of requests.

        :param request: The current request instance.
        :type request: rest_framework.request.Request

        :param view: The view that is currently being accessed
        :type view: rest_framework.views.APIView

        :return: Whether the request should be further processed or not
        :rtype: bool
        """
        identifier = self.get_ident(request)

        cache_timeout = self.get_cache_timeout(
            self.get_tryouts(), self.get_timeout()
        )

        self.timeout = self.get_timeout()
        self.tryouts = self.cache.get_or_set(identifier, (), cache_timeout)

        if self.wait() > 0:
            return False

        truncated = (*self.tryouts, self.timer())[-self.get_tryouts():]
        self.cache.set(identifier, truncated, cache_timeout)
        return True

    def wait(self):
        """
        Calculate the number of seconds to wait until the next request.

        :return: The number of seconds to wait
        :rtype: int
        """
        if not bool(len(self.tryouts)):
            return 0

        timeout = (self.tryouts[-1] + (len(self.tryouts) * self.timeout))
        return timeout - self.timer()

    def get_cache_timeout(self, n, t):
        """
        Calculate the cache timeout.

        Because the timeouts add up recursively we use the
        following formula:

            n
        d = Σ t*i
            i=1

        where:
            d = The cache timeout (deletion time)
            n = The Number of tryouts
            t = The Timeout in seconds

        :param n: The number of tryouts that are available
        :type n: int

        :param t: The timeout in seconds
        :type t: int

        :return: The timeout of the cache in seconds
        :rtype: int
        """
        return sum(t*(i+1) for i in range(0, n))
