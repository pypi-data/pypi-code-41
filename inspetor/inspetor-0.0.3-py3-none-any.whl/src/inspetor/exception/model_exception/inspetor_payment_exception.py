from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorPaymentException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_PAYMENT_ID = {
        'message': 'id is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_PAYMENT_METHOD = {
        'message': 'method is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_PAYMENT_INSTALLMENTS = {
        'message': 'installments is a required property. It should be an integer greater than zero.',
        'code'   : 7003,
    }

    PAYMENT_METHOD_INVALID = {
        'message': 'This payment method is not a valid one.',
        'code'   : 7004,
    }

    REQUIRED_PAYMENT_CREDIT_CARD = {
        'message': 'Credit card can\'t be null when method is credit_card.',
        'code'   : 7005,
    }
