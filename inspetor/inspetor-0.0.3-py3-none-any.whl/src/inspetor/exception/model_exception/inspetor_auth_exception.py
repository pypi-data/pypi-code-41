from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorAuthException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_AUTH_EMAIL = {
        'message': 'account_email is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_AUTH_TIMESTAMP = {
        'message': 'timestamp is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }
