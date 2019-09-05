from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorItemException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_ITEM_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_ITEM_EVENT_ID = {
        'message': 'event_id is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_ITEM_SESSION_ID = {
        'message': 'session_id is a required property. It can\'t be null on creation.',
        'code'   : 7003,
    }

    REQUIRED_ITEM_PRICE = {
        'message': 'price is a required property. It can\'t be null on creation.',
        'code'   : 7004,
    }

    REQUIRED_ITEM_QUANTITY = {
        'message': 'quantity is a required property. It must be an integer greater than zero.',
        'code'   : 7006,
    }

    ITEM_PRICE_INVALID = {
        'message': 'price is not valid. It must be a double value equals or greater than zero.',
        'code'   : 7005,
    }
