import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_RETRIES = 4

# This has to be an excellent approximation to the number of milliseconds for
# a round the world ping. CRITICAL. DON'T CHANGE! (jk)
DEFAULT_BACKOFF_FACTOR = 0.267

DEFAULT_RETRY_STATUS_FORCE_LIST = ()


def requests_retry_session(retries=DEFAULT_RETRIES,
                           backoff_factor=DEFAULT_BACKOFF_FACTOR,
                           status_forcelist=DEFAULT_RETRY_STATUS_FORCE_LIST,
                           raise_on_status=False,
                           session=None):
    """ Get a retryable Python requests session

    See urllib3.util.retry.Retry for a more detailed description of the
    parameters.

    >>> from time import time
    >>> test_url = "https://httpstat.us/418"
    >>>
    >>> # Impatient retrying
    >>> retry_session_impatient = requests_retry_session(backoff_factor=0.01,
    ...                                                  retries=1,
    ...                                                  status_forcelist=(418,),
    ...                                                  raise_on_status=False)
    >>>
    >>> start = time()
    >>> retry_session_impatient.get(test_url)
    <Response [418]>
    >>> duration = time() - start
    >>> duration < 3
    True
    >>>
    >>> # Patient retrying
    >>> retry_session_patient = requests_retry_session(backoff_factor=1.0,
    ...                                                retries=4,
    ...                                                status_forcelist=(418,),
    ...                                                raise_on_status=False)
    >>>
    >>> start = time()
    >>> retry_session_patient.get(test_url)
    <Response [418]>
    >>> duration = time() - start
    >>> duration > 4
    True

    :param int retries: the number of retries
    :param float backoff_factor: the base interval for backing off
    :param tuple[int] status_forcelist: a
    :param bool raise_on_status: when the session is invoked for a request,
        if this is True and the requests fail after the specified number of
        retires, raises a urllib3.exceptions.MaxRetryError
    :param requests.Session session: the initial session to which to attach
        the retrying adapter. If not provided, creates a default
        requests.Session instance
    :return: the session
    :rtype: requests.Session
    :raises: urllib3.exceptions.MaxRetryError
    """
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist,
                  raise_on_status=raise_on_status)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class MissingIDParameter(Exception):
    def __init__(self):
        super().__init__("The 'id' parameter must be included in the request")


class InvalidBaseUrl(Exception):
    def __init__(self):
        super().__init__("The supplied base URL is not a valid string")


class InvalidToken(Exception):
    def __init__(self):
        super().__init__("The supplied API token is not a valid string")


class DRFClient:
    def __init__(self, base_url, token,
                 retries=DEFAULT_RETRIES,
                 backoff_factor=DEFAULT_BACKOFF_FACTOR,
                 status_forcelist=DEFAULT_RETRY_STATUS_FORCE_LIST,
                 raise_on_status=False):

        # If the base_url is an empty string or None type
        if not isinstance(base_url, str) or not base_url:
            raise InvalidBaseUrl

        if not isinstance(token, str) or not token:
            raise InvalidToken

        session = requests_retry_session(retries=retries,
                                         backoff_factor=backoff_factor,
                                         status_forcelist=status_forcelist,
                                         raise_on_status=raise_on_status)
        self.requests = ApiRequest(base_url, token, session=session)
        self.client = Stage(requester=self.requests)


class ApiRequest:
    def __init__(self, base_url, token, session=None):
        self.base_url = base_url
        self.headers = {'Authorization': str(token)}
        if not session:
            session = requests_retry_session()
        self.session = session

    @staticmethod
    def return_response(request_response):
        try:
            response = {
                'status_code': request_response.status_code,
                'response': request_response.json()
            }
        except:
            response = {
                'status_code': request_response.status_code,
                'response': {'text_response': request_response.text}
            }
        return response

    def get_request(self, request_url):
        r = self.session.get(self.base_url + str(request_url),
                             headers=self.headers)
        return self.return_response(r)

    def post_request(self, request_url, data):
        r = self.session.post(self.base_url + str(request_url),
                              json=data, headers=self.headers)
        return self.return_response(r)

    def put_request(self, request_url, data):
        r = self.session.put(self.base_url + str(request_url),
                             json=data, headers=self.headers)
        return self.return_response(r)

    def patch_request(self, request_url, data):
        r = self.session.patch(self.base_url + str(request_url),
                               json=data, headers=self.headers)
        return self.return_response(r)

    def delete_request(self, request_url):
        r = self.session.delete(self.base_url + str(request_url),
                                headers=self.headers)
        return self.return_response(r)


class Stage:
    def __init__(self, requester=None, path=None):
        self.path = path
        self.requester = requester

    def __getattr__(self, path):
        self.path = path
        return self.request

    def request(self, *args, **kwargs):
        request_url = '/{}/'.format(self.path.split('_')[0])

        # Determine the request type (currently based on DRF format)
        # -------------------------------------------------------------------------

        if self.path.endswith('_list'):
            separator = '?'
            for key in kwargs:
                request_url += '{}{}={}'.format(separator, key, kwargs[key])
                if separator == '?':
                    separator = '&'
            return self.requester.get_request(request_url)

        elif self.path.endswith('_read'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.get_request(request_url)

        elif self.path.endswith('_create') and not self.path.endswith('_bulk_create'):

            if len(kwargs) == 0 and len(args) == 1:
                return self.requester.post_request(request_url, args[0])
            else:
                return self.requester.post_request(request_url, kwargs)

        elif self.path.endswith('_partial_update'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.patch_request(request_url, kwargs)

        elif self.path.endswith('_update') and not self.path.endswith('_bulk_update'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.put_request(request_url, kwargs)

        elif self.path.endswith('_delete') and not self.path.endswith('_bulk_delete'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.delete_request(request_url)

        # Dealing with custom (non-DRF) requests. THIS MAY CHANGE IN THE FUTURE
        root_url = self.path.split('_')[0]
        request_url += self.path.replace(root_url, '', 1)[1:] + '/'

        if ('id' in kwargs and len(kwargs) == 1) or (
                len(kwargs) == 0 and len(args) == 0):  # A custom GET request (optionally) with an ID field
            if 'id' in kwargs:
                request_url += str(kwargs['id']) + '/'
            return self.requester.get_request(request_url)

        elif len(kwargs) >= 1 and len(args) == 0:  # A custom POST request
            return self.requester.post_request(request_url, kwargs)

        elif len(args) == 1:  # A custom post request with pre-formatted body data
            return self.requester.post_request(request_url, args[0])

        else:
            raise Exception('Unknown request type')
