from enum import Enum

class ErrorCodes(Enum):
    StreamConnectError = "Stream Connect Error"
    DataCompressionError = "Error occured while compressing {data}"
    DataDecompressionError = "Error occured while de-compressing {data}"


class Error(Exception):
    """Error Class"""

    def __init__(self, error, **kwrags):
        self.error_code = error.name
        self.error_message = error.value.format(**kwrags)

    def get_error(self):
        """Returns the error in dict format"""
        return {
            'error_code': self.error_code,
            'error_message': self.error_message
        }