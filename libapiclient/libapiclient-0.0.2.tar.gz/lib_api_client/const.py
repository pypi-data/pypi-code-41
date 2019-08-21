from libenum import EnumBase


class ResponseType(EnumBase):
    JSON = 'json'
    TEXT = 'text'
    XML = 'document'
    NO_PARSING = 'no_parsing'


SLOW_REQUEST_TIME = 5000
