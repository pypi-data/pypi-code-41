import base64
import json
import zlib

from publish_notifier.errors import Error, ErrorCodes

class Compressor:

    def __init__(self, data):
        self.data = data

    def compress(self):
        """Returns the compressed data"""
        try:
            compressed_data = base64.b64encode(
                zlib.compress(
                    json.dumps(self.data).encode('utf-8')
                )
            ).decode('ascii')
        except ValueError as e:
            raise Error(ErrorCodes.DataCompressionError, data=self.data)
        return compressed_data

    def decompress(self):
        """Decompresses the compressed data"""
        try:
            decompressed_data = zlib.decompress(base64.b64decode(self.data)).decode('utf-8')
        except TypeError as e:
            raise Error(ErrorCodes.DataDecompressionError, data=self.data)
        return decompressed_data
