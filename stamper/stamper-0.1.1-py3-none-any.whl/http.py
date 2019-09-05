
import http.client
from urllib.parse import urlparse, urlencode, quote_plus


class HTTPClient(object):

    def __init__(self, base_url):
        self.parsed_url = urlparse(base_url)
        if self.parsed_url.scheme == 'https':
            self.conn = http.client.HTTPSConnection(self.parsed_url.netloc)
        else:
            self.conn = http.client.HTTPConnection(self.parsed_url.netloc)

    def get(self, url):
        self.conn.request('GET', url)
        response = conn.getresponse()
        return response.read()

    def post(self, url, data):
        encoded_data = urlencode(data, quote_via=quote_plus)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        self.conn.request('POST', url, encoded_data, headers)
        response = conn.getresponse()
        return response.read()
