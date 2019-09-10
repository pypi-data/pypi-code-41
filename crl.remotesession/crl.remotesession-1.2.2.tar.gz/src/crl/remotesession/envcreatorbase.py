import abc
import six


__copyright__ = 'Copyright (C) 2019, Nokia'


@six.add_metaclass(abc.ABCMeta)
class EnvCreatorBase(object):
    @abc.abstractmethod
    def create(self, target, envname):
        """Create environment in *target* with *envname*.

        Return:
            update environment dictionary from *target* to *envname* target
            in *target*.
        """
