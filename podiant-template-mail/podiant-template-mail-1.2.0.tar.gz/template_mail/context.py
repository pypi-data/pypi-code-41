from . import settings
from importlib import import_module


class Message(object):
    recipient = ''
    subject = ''
    sender = ''
    tag = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):  # pragma: no cover
                raise TypeError(
                    '__init__() got an unexpected keyword argument \'%s\'' % (
                        key
                    )
                )

            setattr(self, key, value)


def get_context(**kwargs):
    context = {}
    message = Message(**kwargs)

    for processor in settings.CONTEXT_PROCESSORS:
        module, func = processor.rsplit('.', 1)
        module = import_module(module)
        func = getattr(module, func)
        ctx = func(message)
        context.update(ctx)

    return context
