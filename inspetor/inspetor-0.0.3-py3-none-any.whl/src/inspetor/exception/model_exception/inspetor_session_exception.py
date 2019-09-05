from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorSessionException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_SESSION_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_SESSION_DATETIME = {
        'message': 'datetime is a required property. It can\'t be null.',
        'code'   : 7002,
    }
