"""compatibility serializer fields."""

__all__ = (
    "QRURIField",
)

from rest_framework.serializers import CharField


class QRURIField(CharField):
    """QRURIField for when pillow or qrcode isn't available."""

    def __init__(self, **kwargs):
        """
        Initialize the class.

        :param kwargs: Additional keyword arguments
        :type kwargs: any
        """
        CharField.__init__(self, **kwargs, read_only=True)
