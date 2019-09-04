from mitmproxy import http
from typing import List


class ProxyDelegate:

    def request(self, flow: http.HTTPFlow): pass

    def response(self, flow: http.HTTPFlow): pass


class ProxyPlugin:
    """
    Base plugin implementation  for mitmproxy
    """

    def __init__(self):
        self._requests: List[http.HTTPFlow] = []
        self._delegates: List[ProxyDelegate] = []
        self.proxy = None

    def add_delegate(self, delegate: ProxyDelegate):
        pass

    def load(self, loader):
        pass

    def configure(self, updated):
        pass

    def request(self, flow: http.HTTPFlow):
        self._requests.append(flow)

    def response(self, flow: http.HTTPFlow):
        pass

    def reset(self):
        self._requests = []

    def shutdown(self):
        if self.proxy:
            self.proxy.shutdown()
