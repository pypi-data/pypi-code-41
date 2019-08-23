from functools import wraps
from typing import Type, TypeVar

from aws_lambda_context import LambdaContext

from contract_helper import hydrate_contract

T = TypeVar("T")


def aws_lambda(contract_class: Type[T]):
    def wrapper(function):
        @wraps(function)
        def decorated(event: dict, context: LambdaContext):
            params = hydrate_contract(event, contract_class)
            return_value = function(params, context)

            return return_value

        return decorated

    return wrapper
