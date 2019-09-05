from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging

class TrackerException(ExceptionAbstract):
    status_code = 900
    severity    = logging.CRITICAL

    REQUIRED_PARAMETERS = {
        'message': 'AppId and trackerName are required parameters.',
        'code'   : 9001,
    }

    INVALID_AUTH_CONTEXT = {
        'message': 'Invalid Context! Authentication valid contexts:  \"account_login\", \"account_logout\".',
        'code'   : 9002
    }

    INVALID_ACCOUNT_CONTEXT = {
        'message': 'Invalid Context! Account valid contexts: \"account_create\", \"account_update\", \"account_delete\".',
        'code'   : 9003
    }

    INVALID_SALE_CONTEXT = {
        'message': 'Invalid Context! Sale valid contexts: \"sale_create\", \"sale_update_status\".',
        'code'   : 9005
    }

    INVALID_TRANSFER_CONTEXT = {
        'message': 'Invalid Context! Tranfer valid contexts: \"transfer_create\", \"transfer_update_status\".',
        'code'   : 9006
    }

    INVALID_PASS_CONTEXT = {
        'message': 'Invalid Context! Password request valid contexts: \"password_reset\", \"password_recovery\".',
        'code'   : 9007
    }

    INVALID_EVENT_CONTEXT = {
        'message': 'Invalid Context! Event request valid contexts: \"event_create\", \"event_update\", \"event_delete\".',
        'code'   : 9008
    }