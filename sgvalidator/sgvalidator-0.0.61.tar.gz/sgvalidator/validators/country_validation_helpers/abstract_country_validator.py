from abc import ABCMeta, abstractmethod


class AbstractCountryValidator():
    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, row):
        pass

    @abstractmethod
    def validateState(self, row):
        pass

    @abstractmethod
    def validateZip(self, row):
        pass

    @abstractmethod
    def validatePhone(self, row):
        pass
