"""Serializer for TOTP device."""

__all__ = (
    "TOTPDeviceSerializer",
)

from rest_framework.serializers import ModelSerializer


from rest_multi_factor.serializers import QRURIField
from rest_multi_factor.plugins.totp.models import TOTPDevice


class TOTPDeviceSerializer(ModelSerializer):
    """
    TOTP Device serializer.

    This serializer will try to generate a PNG QR code
    if qrcode and pillow are available.
    """

    class Meta:  # noqa:
        model = TOTPDevice
        fields = ("authenticator_url",)

    authenticator_url = QRURIField()
