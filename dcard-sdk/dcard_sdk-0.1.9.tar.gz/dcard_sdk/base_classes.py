from abc import ABCMeta, abstractmethod

from dcard_sdk.extceptions import ClientError, EAISTOError, MultiError, AuthorizationError, MethodNotExistError, \
    UnexpectedError, UnknownError, ActionNotAllowedError

ERROR_MAP = {
    klass.code: klass
    for klass in
    (AuthorizationError, MethodNotExistError, ClientError, EAISTOError, UnknownError, ActionNotAllowedError)
}


class Response(metaclass=ABCMeta):
    _data = None

    @property
    def data(self) -> dict:
        assert self._data is not None, (
            'You must define `._data`'
        )

        return self._data


class Handler(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Response:
        pass


def get_error(error):
    code, messages = error['code'], error['messages']
    exception_klass = ERROR_MAP.get(code)
    if exception_klass is None:
        return UnexpectedError(code, messages)

    return exception_klass(messages)


class ResponseExt(Response):
    def __init__(self, response):
        content = response.json()
        self._data = self.get_payload(content)

    def get_payload(self, data):
        self.handle_data(data)
        return self.format_data(data)

    def handle_data(self, data):
        errors = data.get('errors', [])
        if errors:
            self.handle_errors(errors)

    def handle_errors(self, errors):
        if len(errors) == 1:
            raise get_error(errors[0])

        raise MultiError(list(map(get_error, errors)))

    def format_data(self, data):
        return {key: value for key, value in data.items() if key != 'errors'}


class HandlerExt(Handler, metaclass=ABCMeta):
    endpoint = None

    def __init__(self, config, request_strategy):
        self.config = config
        self.req_strategy = request_strategy

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def get_url(self, **kwargs):
        assert self.endpoint is not None
        return self.config['BASE_URL'] + self.endpoint.format(**kwargs)

    def default_query_params(self):
        return {
            'api_key': self.config['API_KEY']
        }

    def get(self, url, params=None):
        result_params = self.default_query_params()
        if params is not None:
            result_params.update(params)

        return self.req_strategy.get(url, params=result_params)

    def post(self, url, json=None):
        params = self.default_query_params()
        return self.req_strategy.post(url, json=json, params=params)
