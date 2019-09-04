"""QRCode field to send on the fly generated QR codes."""

__all__ = (
    "QRURIField",
)

import io
import base64


from qrcode import make
from qrcode.image.pil import PilImage

from rest_framework.metadata import SimpleMetadata
from rest_framework.serializers import Field


class QRURIField(Field):
    """
    QR-code generating field.

    This field will generate a QR code for a URI and encode
    it with base 64.
    """

    def __init__(self, **kwargs):
        """
        Initialize the class.

        :param kwargs: The keyword arguments to pass on
        :type kwargs: any
        """
        Field.__init__(self, **kwargs, read_only=True)

    def to_representation(self, uri):
        """
        Generate QR code for a URI and encode it.

        :param uri: The URI to generate for
        :type uri: str

        :return: A base64 encoded image.
        :rtype: bytes
        """
        matrix = make(uri, image_factory=PilImage)
        buffer = io.BytesIO()

        matrix.get_image().save(buffer, "PNG")

        buffer.seek(0)

        return base64.b64encode(buffer.read())

    def to_internal_value(self, data):  # pragma: no cover
        """
        Ignored method, this field is read-only.

        :param data: The data to ignore
        :type data: any
        """
        raise NotImplementedError("This method must be overridden")


# Register the field within the metadata for rendering support
SimpleMetadata.label_lookup[QRURIField] = "base64/png"
