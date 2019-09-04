"""Serializer for HOTP device."""

__all__ = (
    "HOTPDeviceSerializer",
)

from rest_framework.serializers import ModelSerializer

from rest_multi_factor.serializers import QRURIField
from rest_multi_factor.plugins.hotp.models import HOTPDevice


class HOTPDeviceSerializer(ModelSerializer):
    """
    HOTP Device serializer.

    This serializer will try to generate a PNG QR code
    if qrcode and pillow are available.
    """

    class Meta:  # noqa:
        model = HOTPDevice
        fields = ("authenticator_url",)

    authenticator_url = QRURIField()
