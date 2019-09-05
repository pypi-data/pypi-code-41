from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorSaleException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_SALE_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_SALE_ACCOUNT_ID = {
        'message': 'account_id is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_SALE_STATUS = {
        'message': 'status is a required property. It can\'t be null on creation.',
        'code'   : 7003,
    }

    REQUIRED_SALE_TIMESTAMP = {
        'message': 'timestamp is a required property. It can\'t be null.',
        'code'   : 7005,
    }

    REQUIRED_SALE_ITEMS = {
        'message': 'items is a required property. It can\'t be null neither an empty array on creation.',
        'code'   : 7006,
    }

    REQUIRED_SALE_PAYMENT = {
        'message': 'payment is a required property. It can\'t be null on creation.',
        'code'   : 7007,
    }

    REQUIRED_SALE_ANALYZED_BY = {
        'message': 'analyzed_by is a required property. It can\'t be null on update.',
        'code'   : 7010,
    }

    SALE_STATUS_INVALID = {
        'message': 'The status is not a valid one.',
        'code'   : 7008,
    }

    SALE_ITEM_PRICE_INVALID = {
        'message': 'One or more items have invalid price.',
        'code'   : 7009,
    }

    REQUIRED_SALE_IS_FRAUD = {
        'message': 'analyzed_by is a required property. It can\'t be null on update.',
        'code'   : 7004,
    }
