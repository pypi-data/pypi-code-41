import contextlib

__version__ = '1.1.0'

def attr(*args, **kwargs):
    '''
    Decorator that adds attributes to classes or functions
    for use with the Attribute (-a) plugin.

    From nose.plugins.attrib. No idea why this is not in nose2.

    '''
    def wrap_ob(ob):
        for name in args:
            setattr(ob, name, True)
        for name, value in kwargs.iteritems():
            setattr(ob, name, value)
        return ob
    return wrap_ob

def speed(label):
    '''
    Decorator for test speed classification (attr was not working well).

    Suggested use is to import speed and decorate with speed.fast etc, rather
    than pass label strings directly:

    import unittest
    from bodylabs.util.test import speed

    @speed.slow
    class TestMySlowClass(unittest.TestCase):

        def test_some_slow_function(self):
            ... # no decorator: gets 'slow' from class

        @speed.veryslow
        def test_some_veryslow_function(self):
            ... # method decorator overrides class decorator
    '''
    def wrap_obj(obj):
        import inspect
        if inspect.ismethod(obj) or inspect.isfunction(obj):
            return _method_speed(label)(obj)
        elif inspect.isclass(obj):
            return _class_speed(label)(obj)
        else:
            raise ValueError('Should only decorate class or function/method, not {}'.format(obj))
    return wrap_obj

speed.fast = speed('fast')
speed.slow = speed('slow')
speed.veryslow = speed('veryslow')
speed.superslow = speed('superslow')

def _method_speed(label):
    '''
    Function/method case helper for @speed
    '''
    def wrap_method(method):
        import functools
        # It is annoying that we have to copy method as wrapped_method instead of just setting attributes directly
        # on method. But that was failing (only from inside class_speed decorator) with:
        # AttributeError: 'instancemethod' object has no attribute '_test_speed'
        def wrapped_method(*args, **kwargs):
            return method(*args, **kwargs)
        setattr(wrapped_method, '_test_speed', label)
        return functools.update_wrapper(wrapped_method, method)
    return wrap_method

def _class_speed(label):
    '''
    Class case helper for @speed. Reaches into the class and calls
    _method_speed on each test method.
    '''
    def wrap_class(cls):
        import inspect
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if name.startswith('test'):
                if getattr(method, '_test_speed', None) is None:
                    setattr(cls, name, _method_speed(label)(method))
        return cls
    return wrap_class

@contextlib.contextmanager
def supress_output(using_mock=True):
    '''
    How to use this:

        from bltest import supress_output

        with supress_output():
            do_something_which_prints()
            print "None of this output will appear"

    '''
    import os
    import sys
    savestderr = sys.stderr
    savestdout = sys.stdout
    class Devnull(object):
        def write(self, _):
            pass
    file_to_use = Devnull() if using_mock else open(os.devnull)
    sys.stderr = file_to_use
    sys.stdout = file_to_use
    yield
    if not using_mock:
        file_to_use.close()
    sys.stderr = savestderr
    sys.stdout = savestdout

def skip_if_ci():
    import os
    import unittest
    if 'CIRCLECI' in os.environ:
        raise unittest.SkipTest("Skipping tests that just don't work in CI")

def skip_if_unavailable(what):
    import unittest
    from baiji.config import is_available as s3_is_available
    from baiji.util.reachability import internet_reachable
    if what == 'internet' or 'internet' in what:
        if not internet_reachable():
            raise unittest.SkipTest('Skipping tests that require access to the internet, since it cannot be reached')
    elif what == 's3' or 's3' in what:
        if not s3_is_available():
            raise unittest.SkipTest('Skipping tests that require s3, since it cannot be reached')
    else:
        raise ValueError("skip_if_unavailable: don't know how to check {}".format(what))

def skip_on_import_error(what):
    import unittest
    from importlib import import_module
    try:
        import_module(what)
    except ImportError:
        raise unittest.SkipTest('Skipping tests that require {}, since it cannot be imported'.format(what))

class BackupEnvMixin(object):
    '''
    Add this to your test case to let you back up and restore environemnt variables
    '''
    def backup_env(self, *env_vars_to_backup):
        import os
        if not hasattr(self, 'old_env'):
            self.old_env = {}  # FIXME pylint: disable=attribute-defined-outside-init
        for var in env_vars_to_backup:
            if var in os.environ:
                self.old_env[var] = os.environ[var]
            else:
                self.old_env[var] = None

    def restore_env(self, *env_vars_to_backup):
        import os
        for var in env_vars_to_backup:
            if self.old_env[var] != None:
                os.environ[var] = self.old_env[var]
            else:
                del os.environ[var]


class SuppressLoggingMixin(object):
    '''
    Add this to your test case, and it will automatically
    suppress output of loggers during your tests.

    You can call self.enable_logging(True) to selectively
    re-enable logging, if needed.

    If you override setUp or tearDown, you MUST invoke
    super.

    '''

    def setUp(self):
        super(SuppressLoggingMixin, self).setUp()
        self.enable_logging(False)

    def tearDown(self):
        super(SuppressLoggingMixin, self).tearDown()
        self.enable_logging(True)

    def enable_logging(self, enabled):
        import logging
        if enabled:
            logging.disable(logging.NOTSET)
        else:
            logging.disable(logging.CRITICAL)
