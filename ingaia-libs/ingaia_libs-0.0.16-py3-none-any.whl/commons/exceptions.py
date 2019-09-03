"""
Common exception classes
"""


class GenericException(Exception):
    message = None

    def __init__(self, message=None):
        self.message = message
        super(GenericException, self).__init__(self.message)
