"""Additional serializer fields."""

__all__ = (
    "QRURIField",
)

try:  # pragma: no cover
    from rest_multi_factor.serializers.fields.qrcode import QRURIField

except ImportError:  # pragma: no cover
    from rest_multi_factor.serializers.fields.compat import QRURIField

