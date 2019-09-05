from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorEventException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_EVENT_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_EVENT_NAME = {
        'message': 'name is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_EVENT_TIMESTAMP = {
        'message': 'timestamp is a required property. It can\'t be null.',
        'code'   : 7003,
    }

    REQUIRED_EVENT_CREATOR_ID = {
        'message': 'creator_id is a required property. It can\'t be null on creation',
        'code'   : 7004,
    }

    REQUIRED_EVENT_ADDRESS = {
        'message': 'address is a required property when the event has physical place.  It can\'t be null on creation.',
        'code'   : 7005,
    }

    REQUIRED_EVENT_SESSIONS = {
        'message': 'sessions is a required property. It can\'t be null neither an empty array on creation.',
        'code'   : 7006,
    }

    REQUIRED_EVENT_SEATING_OPTIONS = {
        'message': 'seating_options should be null or an array of strings.',
        'code'   : 7007,
    }

    REQUIRED_EVENT_CATEGORIES = {
        'message': 'categories should be null or an array of strings.',
        'code'   : 7008,
    }

    EVENT_STATUS_INVALID = {
        'message': 'The status is not a valid one.',
        'code'   : 7009,
    }

    REQUIRED_EVENT_ADMINS_ID = {
        'message': 'admins_id should be an array of one or more users.',
        'code'   : 7012,
    }

    REQUIRED_EVENT_IS_PHYSICAL = {
        'message': 's_physical should be a boolean. It\'s true by default',
        'code'   : 7013,
    }
