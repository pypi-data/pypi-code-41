"""Abstract base class for algorithm implementations."""

__all__ = (
    "AbstractAlgorithm",
)

from abc import ABCMeta, abstractmethod


from rest_multi_factor.settings import multi_factor_settings


class AbstractAlgorithm(metaclass=ABCMeta):
    """Abstract base class for algorithm implementations."""

    should_validate = multi_factor_settings.ALGORITHM_RFC_VALIDATION

    @abstractmethod
    def calculate(self, *args, **kwargs):
        """
        Calculate The algorithm.

        :param args: The required arguments (vary)
        :type args: tuple

        :param kwargs: The required keyword arguments (vary)
        :type kwargs: dict

        :return: The return value of the algorithm
        :rtype: str | int
        """

    @abstractmethod
    def validate(self, *args, **kwargs):
        """
        Validate if the arguments provided are allowed.

        :param args: The algorithms arguments (vary)
        :type args: tuple

        :param kwargs: The algorithms keyword arguments (vary)
        :type kwargs: dict

        :raises rest_multi_factor.exceptions.RFCGuidanceException:
            If a required RFC guidance is not followed
        """
