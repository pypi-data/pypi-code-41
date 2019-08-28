import os
from zappa.async import run as zappa_run
from django.conf import settings



def run(function, **kwargs):
    def wrapper(**kwargs):
        if "kwargs" in kwargs:
            kwargs = kwargs['kwargs']
        return function(**kwargs)
    if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        return wrapper(**kwargs)
    zappa_run(wrapper, kwargs=kwargs)
    return True