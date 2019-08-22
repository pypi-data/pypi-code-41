from abc import ABCMeta, abstractmethod
from .validator_status import ValidatorStatus


class AbstractValidator:
    __metaclass__ = ABCMeta

    def run(self):
        self.announce()
        return self.validate()

    @abstractmethod
    def announce(self):
        pass

    @abstractmethod
    def subvalidators(self):
        """
        Returns a list of each subvalidator implemented by the validator
        """
        return []

    def validate(self):
        res = [func() for func in self.subvalidators()]
        failures = list(filter(lambda x: x == ValidatorStatus.FAIL, res))
        if len(failures) > 0:
            return ValidatorStatus.FAIL
        return ValidatorStatus.SUCCESS

    def subvalidatorName(self, subvalidator):
        return "{}:{}".format(self._className(), subvalidator.__name__)

    def _className(self):
        return self.__class__.__name__
