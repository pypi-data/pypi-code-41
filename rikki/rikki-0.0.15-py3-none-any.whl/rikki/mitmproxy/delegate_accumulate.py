from typing import Optional, List

from mitmproxy import http

from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.plugin import ProxyDelegate
from rikki.mitmproxy.util import filter


class AccumulateFilterConfig:

    def __init__(
            self,
            request: Optional[Request] = None,
            response: Optional[Response] = None
    ) -> None:
        super().__init__()
        self.request = request
        self.response = response


class Accumulate(ProxyDelegate):

    def __init__(self, filter_config: AccumulateFilterConfig):
        """
        This plugin will accumulate all flows filtered with the config. Be aware that flow will appear in results
        with delay in case when you specify response in filter config
        :param filter_config: request and response data, that will be used to filter requests
        """
        super().__init__()
        self.__config = filter_config
        self.accumulated_items: List[http.HTTPFlow] = []

    def request(self, flow: http.HTTPFlow):
        if self.__config.request and not self.__config.response:
            self.accumulated_items.extend(filter([flow], request=self.__config.request))

    def response(self, flow: http.HTTPFlow):
        if self.__config.response:
            self.accumulated_items.extend(
                filter(
                    [flow],
                    request=self.__config.request,
                    response=self.__config.response
                )
            )
