import logging
import time

from requests.cookies import RequestsCookieJar
from swissarmykit.req.RequestBase import RequestBase


class HeadersUtils(RequestBase):

    def __init__(self):
        super().__init__()
        self._has_br = False
        self.extra_headers = {}
        self._is_upper_case_key = True

    def init_default(self):
        self.extra_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }

    def set_headers(self, headers_str=None):
        for h in headers_str.splitlines():
            header = h.strip()
            if h:
                k_v = header.split(':', 1)
                if len(k_v) == 2:
                    self.extra_headers[k_v[0].strip()] = k_v[1].strip()
        self._validate()

        if self.extra_headers:
            _c = list(self.extra_headers.keys())[0][0]
            self._is_upper_case_key = _c == _c.upper()

    def reset_headers(self):
        self.extra_headers = {}

    def set_cookies(self, cookie_jar):
        cookie_dict = cookie_jar.get_dict()
        found = ['%s=%s' % (name, value) for name, value in cookie_dict.items()]
        _v = '; '.join(found)
        _k = ''
        has_cookie = False
        for k in ['Cookie', 'cookie']:
            if k in self.extra_headers:
                self.extra_headers[k] = _v
                _k = k
                has_cookie = True

        if not has_cookie:
            _k = 'Cookie' if self._is_upper_case_key else 'cookie'
            self.extra_headers[_k] = _v

        return {_k: _v}

    def get_headers(self, override_headers: dict = None):
        '''
        :param override_headers:  override on each request
        :return: headers:
        '''
        # Clone the template.
        if not self.extra_headers:
            self.init_default()
            print('INFO: set default headers ', self.extra_headers)

        headers = self.extra_headers.copy()

        # Add extra User-Agent if not has
        if not (self.extra_headers.get('user-agent') and self.extra_headers.get('User-Agent')):
            ua_header = self.get_user_agent()
            for k, v in ua_header.items():
                headers[k] = v

        # Override for purpose
        if override_headers:
            for k, v in override_headers.items():
                headers[k] = str(v)  # Must str: Page: 1 , 1 is string

        return headers

    def _get_kw(self, url, override_headers: dict = None, **kwargs):
        self._before_request(url)
        kwargs = {'headers': self.get_headers(override_headers), **kwargs}

        if self.timeout:
            kwargs['timeout'] = self.timeout

        if self.proxy:
            kwargs['proxies'] = self.proxy.get_proxies()

        if self.is_disable_verify:
            self.log.warn('WARN: set verify=False for requests')
            kwargs['verify'] = False

        if self.is_use_proxies:
            p = self.get_unused_proxy()
            while not p:
                time.sleep(5)
                p = self.get_unused_proxy()
                print(',_,', end='', flush=True)
            kwargs['proxies'] = p.get_proxies()

        if self.is_debug:
            logging.basicConfig(level=logging.DEBUG)
            print('Debug - Request Headers: ', kwargs)
        return kwargs

    def _validate(self):
        # Remove :         accept-encoding: gzip, deflate, br  [accept-encoding: gzip, deflate, br: => br: Brotli compress]')
        for h_ in ['accept-encoding', 'Accept-Encoding']:
            if h_ in self.extra_headers and 'br' in self.extra_headers.get(h_):
                v_ = [i.strip() for i in self.extra_headers.get(h_).split(',')]
                v_.remove('br')
                self.extra_headers[h_] = ', '.join(v_)
