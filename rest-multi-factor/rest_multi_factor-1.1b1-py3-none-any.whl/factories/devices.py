"""Factories for tests's devices."""

__all__ = (
    "PSDeviceFactory",
    "PSChallengeFactory",
    "DiDeviceFactory",
    "DiChallengeFactory",
)

from factory import DjangoModelFactory, SubFactory

from tests.models import PSChallenge, PSDevice
from tests.models import DiChallenge, DiDevice

from rest_multi_factor.factories.auth import AuthFactory


class PSDeviceFactory(DjangoModelFactory):
    """Pre Shared value Device Factory."""

    class Meta:
        model = PSDevice


class PSChallengeFactory(DjangoModelFactory):
    """Pre Shared value Challenge Factory."""

    class Meta:
        model = PSChallenge

    token = SubFactory(AuthFactory)
    device = SubFactory(PSDeviceFactory)


class DiDeviceFactory(DjangoModelFactory):
    """Dispatchable Device Factory."""

    class Meta:
        model = DiDevice


class DiChallengeFactory(DjangoModelFactory):
    """Dispatchable Challenge Factory."""

    class Meta:
        model = DiChallenge

    token = SubFactory(AuthFactory)
    device = SubFactory(DiDeviceFactory)
