from __future__ import (
    absolute_import,
    unicode_literals,
)

from conformity.error import (
    ERROR_CODE_INVALID,
    ERROR_CODE_MISSING,
    ERROR_CODE_UNKNOWN,
)


__all__ = (
    'ERROR_CODE_ACCESS_DENIED',
    'ERROR_CODE_INVALID',
    'ERROR_CODE_MISSING',
    'ERROR_CODE_NOT_AUTHORIZED',
    'ERROR_CODE_NOT_FOUND',
    'ERROR_CODE_RESPONSE_NOT_SERIALIZABLE',
    'ERROR_CODE_RESPONSE_TOO_LARGE',
    'ERROR_CODE_SERVER_ERROR',
    'ERROR_CODE_UNKNOWN',
)


ERROR_CODE_ACCESS_DENIED = 'ACCESS_DENIED'
ERROR_CODE_NOT_AUTHORIZED = 'NOT_AUTHORIZED'
ERROR_CODE_NOT_FOUND = 'NOT_FOUND'
ERROR_CODE_RESPONSE_NOT_SERIALIZABLE = 'RESPONSE_NOT_SERIALIZABLE'
ERROR_CODE_RESPONSE_TOO_LARGE = 'RESPONSE_TOO_LARGE'
ERROR_CODE_SERVER_ERROR = 'SERVER_ERROR'
