import abc
import six


@six.add_metaclass(abc.ABCMeta)
class KerasCallbackBase(object):
    @property
    @abc.abstractmethod
    def _model(self):
        pass
