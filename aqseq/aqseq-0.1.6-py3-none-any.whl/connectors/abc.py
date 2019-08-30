import abc


class Connector(abc.ABC):
    # rule, everything takes a jdna object

    @abc.abstractmethod
    def to_api(self):
        pass

    @abc.abstractmethod
    def from_api(self):
        pass

    @abc.abstractmethod
    def push(self):
        pass

    @abc.abstractmethod
    def fetch(self):
        pass


class Registry(Connector):
    @abc.abstractmethod
    def _format_uid(self):
        pass

    @abc.abstractmethod
    def find(self):
        pass

    @abc.abstractmethod
    def register(self, seq, uid, overwrite=True):
        pass
