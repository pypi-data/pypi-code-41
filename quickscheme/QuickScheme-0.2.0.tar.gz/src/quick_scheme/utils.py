''' Utilities '''
import logging

LOG = logging.getLogger(__name__)


class Args(object):
    ''' Argument Holder '''

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def run(self, function, default=None):
        ''' Run a runable function'''
        if callable(function):
            return function(*self.args, **self.kwargs)
        return default
