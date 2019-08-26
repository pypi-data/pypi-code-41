from time import time

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class CipSession(Session):
    """
    Extending requests.Session object adding adapters, event hooks and timeout 
    to all requests made, usage:
    
        >>> cip_requests = CipSession(retries=3, timeout=30, logger=app.log)
        >>> cip_requests.get('http://example.url')
        <Response [200]>
    """

    ERRORS = (400, 403, 404, 500, 502, 503, 504)
    BACKOFF_FACTOR = 0.3

    def __init__(self, retries=0, timeout=None, logger=None, **kwargs):
        self.timeout = timeout
        self.logger = logger

        super().__init__(**kwargs)

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=self.BACKOFF_FACTOR,
            status_forcelist=self.ERRORS,
            raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retry)
        self.mount('http://', adapter)
        self.mount('https://', adapter)

        if self.logger:
            self.hooks['response'].append(self.log_request)

    def request(self, *args, **kwargs):
        self.request_time = time()
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = self.timeout
        response_object = super().request(*args, **kwargs)
        return response_object

    def log_request(self, r, *args, **kwargs):
        prefix = '::cipcore::CipSession::log_request::'
        message = (
            f'{prefix}Request {r.request.method} {r.url} '
            f'with status {r.status_code} {r.reason} '
            f'and took {round(time() - self.request_time, 2)} seconds'
        )
        self.logger.info(status=200, message=message)
