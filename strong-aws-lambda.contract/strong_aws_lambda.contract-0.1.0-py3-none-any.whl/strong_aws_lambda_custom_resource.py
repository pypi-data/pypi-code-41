from functools import wraps
from typing import Type, TypeVar

from aws_lambda_context import LambdaContext

from contract_helper import hydrate_contract

T = TypeVar("T")


def aws_lambda_custom_resource(contract_class: Type[T], handle_exceptions: bool = True):
    def wrapper(function):
        @wraps(function)
        def decorated(event: dict, context: LambdaContext):
            return_value = None
            try:
                params = hydrate_contract(event, contract_class)
                return_value = function(params, context)
            except Exception as ex:
                if handle_exceptions:
                    return {'Status': 'FAILED', 'Reason': str(ex)}

            return return_value

        return decorated

    return wrapper
