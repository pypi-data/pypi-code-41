"""Serializers to serialize device instances and classes."""

__all__ = (
    "DeviceSerializer",
    "RegisterSerializer",
)

from rest_framework.serializers import Serializer, CharField
from rest_framework.serializers import BooleanField, IntegerField


class DeviceSerializer(Serializer):
    """
    Serializers for device metadata.

    This serializer serializes information like whether
    or not the device is already confirmed and the name.
    """

    update = None
    create = None

    index = IntegerField(read_only=True)
    confirmed = BooleanField(read_only=True)
    verbose_name = CharField(read_only=True)
    dispatchable = BooleanField(read_only=True)


class RegisterSerializer(Serializer):
    """Serializer for registering devices."""

    update = None
    create = None

    registered = BooleanField(read_only=True)
    verbose_name = CharField(read_only=True)
