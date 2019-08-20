

def singleton(klass):
    assert type(klass) == type(object), 'Incorrect usage of singleton decorator'

    class _Singleton(object):
        __instance = None
        __klass = klass

        def __init__(self, *args, **kwargs):
            if self.__class__.__instance is None:
                self.__class__.__instance = self.__class__.__klass(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            return self.__class__.__instance

        def __getattr__(self, item):
            return getattr(self.__class__.__instance, item)

        def __setattr__(self, key, value):
            setattr(self.__class__.__instance, key, value)

    return _Singleton
