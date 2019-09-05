from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorGeneralException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    WRONG_TIMESTAMP_TYPE = {
        'message': 'The timestamp should be an integer.',
        'code'   : 7001,
    }
