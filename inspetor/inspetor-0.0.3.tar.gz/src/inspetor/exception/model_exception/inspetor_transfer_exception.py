from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorTransferException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_TRANSFER_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_TRANSFER_TIMESTAMP = {
        'message': 'timestamp is a required property. It can\'t be null.',
        'code'   : 7002,
    }

    REQUIRED_TRANSFER_ITEM_ID = {
        'message': 'item_id is a required property. It can\'t be null on creation.',
        'code'   : 7003,
    }

    REQUIRED_TRANSFER_ACCOUNT_ID = {
        'message': 'sender_account_id is a required property. It can\'t be null on creation',
        'code'   : 7004,
    }

    REQUIRED_TRANSFER_ID_RECEIVER_EMAIL = {
        'message': 'receiver_email is a required property. It can\'t be null on creation.',
        'code'   : 7005,
    }

    TRANSFER_STATUS_INVALID = {
        'message': 'That\'s an invalid status.',
        'code'   : 7006,
    }
