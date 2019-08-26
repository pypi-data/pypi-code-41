"""Backends for checking how many verifications are needed."""

__all__ = (
    "DefaultBackend",
    "AbstractVerificationBackend",
)

from abc import ABCMeta, abstractmethod


from django import VERSION
from django.db.models.query import Q


from rest_multi_factor.utils import unify_queryset
from rest_multi_factor.models import Challenge
from rest_multi_factor.settings import multi_factor_settings


class AbstractVerificationBackend(metaclass=ABCMeta):
    """Abstract base class for verifications backends."""

    @abstractmethod
    def verify(self, token, view):
        """
        Get the number of verifications left.

        :param token: The token to check
        :type token: rest_framework.authtoken.Token | knox.model.AuthToken

        :param view: The current view
        :type view: rest_framework.views.APIView

        :return: The number of verifications left
        :rtype: int
        """

    def get_verifications(self):
        """
        Get the number of verifications required.

        Without this only two-factor would be available.

        :return: The number of verifications required
        :rtype: int
        """
        verifications = multi_factor_settings.REQUIRED_VERIFICATIONS

        assert isinstance(verifications, int) and verifications > 0, (
            "'REQUIRED_VERIFICATIONS' MUST be a non-zero positive integer not"
            " '{0}', you could also configure another backend.>"
            .format(verifications)
        )

        return verifications


class DefaultBackend(AbstractVerificationBackend):
    """
    Default backend for calculating number of verifications left.

    This class shouldn't be replaced in most cases, but can be if
    you wan't to enable/disable multi factor authentication through
    for example models.
    """

    def verify(self, token, view):
        """
        Verify how many verifications are needed.

        :param token: The token to check
        :type token: rest_framework.authtoken.Token | knox.model.AuthToken

        :param view: The current view
        :type view: rest_framework.views.APIView | None

        :return: The number of verifications left
        :rtype: int
        """
        filter = Q(token=token) & Q(confirm=True)
        queryset = unify_queryset(Challenge, fields=("id",), filter=filter)

        # ticket: https://code.djangoproject.com/ticket/28399
        if VERSION < (1, 11, 4):
            return self.get_verifications() - len(queryset)  # pragma: no cover

        return self.get_verifications() - queryset.count()  # pragma: no cover
