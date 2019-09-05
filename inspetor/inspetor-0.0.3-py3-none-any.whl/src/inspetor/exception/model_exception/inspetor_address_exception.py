from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorAddressException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_ADDRESS_STREET = {
        'message': 'street is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_ADDRESS_ZIPCODE = {
        'message': 'zip_code is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_ADDRESS_CITY = {
        'message': 'city is a required property. It can\'t be null.',
        'code'   : 7003,
    }

    REQUIRED_ADDRESS_STATE = {
        'message': 'state is a required property. It can\'t be null.',
        'code'   : 7004,
    }

    REQUIRED_ADDRESS_COUNTRY = {
        'message': 'country is a required property. It can\'t be null.',
        'code'   : 7005,
    }