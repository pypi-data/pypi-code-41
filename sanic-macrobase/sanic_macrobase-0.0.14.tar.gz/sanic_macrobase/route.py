from typing import Iterable

from sanic_macrobase.endpoint import SanicEndpoint
from sanic_macrobase.exceptions import RoutingErrorException


class Route(object):
    """
    Base route for HTTP sanic server
    """
    def __init__(self, handler: SanicEndpoint, uri, methods=frozenset({'GET'}), host=None,
                  strict_slashes=None, version=None, name=None):
        super(Route, self).__init__()

        if not isinstance(handler, SanicEndpoint):
            raise RoutingErrorException('Handler must be instance of SanicEndpoint class')

        self._handler = handler
        self._uri = uri
        self._methods = methods
        self._host = host
        self._strict_slashes = strict_slashes
        self._version = version

        self._name = name
        if self._name is None:
            self._name = self._handler.__name__

    @property
    def handler(self) -> SanicEndpoint:
        return self._handler

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def methods(self) -> Iterable:
        return self._methods

    @property
    def host(self) -> str:
        return self._host

    @property
    def strict_slashes(self) -> bool:
        return self._strict_slashes

    @property
    def version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return self._name
