import sys
import inspect


def asdict(cls):
    """Helper to create a dictionary out of the class attributes (fields/variables)"""
    return {k: v for k, v in cls.__class__.__dict__.items()
            if not k.startswith('_')
            and not inspect.isfunction(v)
            and not inspect.ismethod(v)}


def schema_decorator(decorators_state, cls):
    """Adds cls to decorator_state"""
    decorators_state['schema'] = cls()
    return cls


class MetaSchema(type):
    """
    Validate, cast types, wrap configuration and invoke 'post_hook' method for
    the Schema class
    """

    def __new__(mcs, name, bases, namespace, **kwds):
        cls = type.__new__(mcs, name, bases, namespace)

        # Parsing type descriptors
        if '__annotations__' in namespace:
            for ann, t in namespace['__annotations__'].items():
                # Validation
                try:
                    setattr(cls, ann, t(namespace[ann]))
                except TypeError as ex:
                    print('given parameters or defined defaults were of incorrect type:')
                    # print(f'{cls.__qualname__}.{ann} -> {ex.args}')  # f-strings require >=3.6
                    print('{}.{} -> {}'.format(cls.__qualname__, ann, ex.args))
                    sys.exit(1)

        # TODO: Maybe check that given parameters matched the schema?
        # Even a fuzzy search to suggest close matches

        cls._wrap(cls)

        # post init hook
        cls.post_init(cls)
        return cls

    def __init__(cls, name, bases, namespace, **kwds):
        super().__init__(name, bases, namespace)
