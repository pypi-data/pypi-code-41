from six import with_metaclass


class __MetaVoid(type):
    def __getattr__(cls, *args, **kwargs):
        return cls

    def __call__(cls, *args, **kwargs):
        return cls

    def __getitem__(cls, *args, **kwargs):
        return cls

    def __setitem__(cls, *args, **kwargs):
        pass

    def __enter__(cls, *args, **kwargs):
        return cls

    def __exit__(cls, *args, **kwargs):
        return None

    def __str__(cls, *args, **kwargs):
        return 'Void'

    def __repr__(cls, *args, **kwargs):
        return ''

    def __iter__(cls, *args, **kwargs):
        return cls

    def __next__(cls, *args, **kwargs):
        raise StopIteration

    def next(cls, *args, **kwargs):
        return cls.__next__(cls, *args, **kwargs)


class Void(with_metaclass(__MetaVoid, object)):
    def __new__(cls, *args, **kwargs):
        return cls
