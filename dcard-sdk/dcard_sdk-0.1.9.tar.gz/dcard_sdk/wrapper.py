from enum import Enum, auto as a
from types import MappingProxyType

from requests import Session

from dcard_sdk.actions import CreateCardRequest, RetrieveCardRequest, ListCities, ListTires, PushCard, UpdateCard, \
    DenyCard, Print, Download


class RequestStrategy:
    def __init__(self, timeout):
        self.timeout = timeout
        self.session = Session()

    def get(self, url, **kwargs):
        return self.session.get(url, **self._get_kwargs(kwargs))

    def post(self, url, **kwargs):
        return self.session.post(url, **self._get_kwargs(kwargs))

    def _get_kwargs(self, kwargs):
        return {'timeout': self.timeout, **kwargs}


class Handlers(Enum):
    CREATE_CARD_REQUEST = a()
    RETRIEVE_CARD_REQUEST = a()
    LIST_CITIES = a()
    LIST_TIRES = a()
    PUSH_CARD = a()
    UPDATE_CARD = a()
    DENY_CARD = a()
    PRINT = a()
    DOWNLOAD = a()


HANDLERS_MAP = {
    Handlers.CREATE_CARD_REQUEST: CreateCardRequest,
    Handlers.RETRIEVE_CARD_REQUEST: RetrieveCardRequest,
    Handlers.LIST_CITIES: ListCities,
    Handlers.LIST_TIRES: ListTires,
    Handlers.PUSH_CARD: PushCard,
    Handlers.UPDATE_CARD: UpdateCard,
    Handlers.DENY_CARD: DenyCard,
    Handlers.PRINT: Print,
    Handlers.DOWNLOAD: Download,
}


class APIWrapper:
    BASE_SETTINGS = MappingProxyType({
        'BASE_URL': 'https://dcard.ws/api',
        'TIMEOUT': 60,
        'TEMPLATE_ID': 3
    })

    def __init__(self, config_dict):
        config_dict = MappingProxyType(
            {**self.BASE_SETTINGS, **config_dict}
        )
        request_strategy = RequestStrategy(config_dict['TIMEOUT'])

        self._handlers = {
            enum_key: handler_class(config_dict, request_strategy)
            for enum_key, handler_class in HANDLERS_MAP.items()
        }

    def create_card_request(self, data):
        handler = self._handlers[Handlers.CREATE_CARD_REQUEST]
        return handler(data)

    def retrieve_card_request(self, public_id):
        handler = self._handlers[Handlers.RETRIEVE_CARD_REQUEST]
        return handler(public_id)

    def push_card(self, public_id, data):
        handler = self._handlers[Handlers.PUSH_CARD]
        return handler(public_id, data)

    def deny(self, public_id):
        handler = self._handlers[Handlers.DENY_CARD]
        return handler(public_id)

    def list_cities(self):
        handler = self._handlers[Handlers.LIST_CITIES]
        return handler()

    def list_tires(self):
        handler = self._handlers[Handlers.LIST_TIRES]
        return handler()

    def print(self, public_id):
        handler = self._handlers[Handlers.PRINT]
        return handler(public_id)

    def download(self, url):
        handler = self._handlers[Handlers.DOWNLOAD]
        return handler(url)
