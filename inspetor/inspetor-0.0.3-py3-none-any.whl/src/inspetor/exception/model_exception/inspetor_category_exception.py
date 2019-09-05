from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorCategoryException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_CATEGORY_ID = {
        'message': 'account_email is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_CATEGORY_EMAIL = {
        'message': 'timestamp is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

