from io import IOBase

import six


class RESTResponse(IOBase):
    def __init__(self, resp):
        self.urllib3_response = resp
        self.status: int = resp.status
        self.reason = resp.reason
        self.data = resp.data

        if six.PY3:
            self.data = self.data.decode('utf8')

    def getheaders(self):
        """Returns a dictionary of the response headers."""
        return self.urllib3_response.getheaders()

    def getheader(self, name, default=None):
        """Returns a given response header."""
        return self.urllib3_response.getheader(name, default)