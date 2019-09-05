from src.inspetor.exception.exception_abstract import ExceptionAbstract

import logging


class InspetorCreditCardException(ExceptionAbstract):
    status_code = 700
    severity    = logging.CRITICAL

    REQUIRED_CREDIT_CARD_SIX = {
        'message': 'first_six_digits is a required property. It can\'t be null.',
        'code'   : 7001,
    }

    REQUIRED_CREDIT_CARD_FOUR = {
        'message': 'last_four_digits is a required property. It can\'t be null on creation.',
        'code'   : 7002,
    }

    REQUIRED_CREDIT_CARD_HOLDER_NAME = {
        'message': 'holder_name is a required property. It can\'t be null on creation.',
        'code'   : 7003,
    }

    REQUIRED_CREDIT_CARD_HOLDER_CPF = {
        'message': 'holder_cpf is a required property. It can\'t be null on creation.',
        'code'   : 7004,
    }

    REQUIRED_CREDIT_CARD_ADDRESS = {
        'message': 'billing_address is a required property. It can\'t be null on creation.',
        'code'   : 7005,
    }

