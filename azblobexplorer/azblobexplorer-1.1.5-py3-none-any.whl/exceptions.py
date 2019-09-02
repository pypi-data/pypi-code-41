
class NoBlobsFound(Exception):
    """
    This exception is raised when there are no blobs.
    """
    def __init__(self, message, errors=None):
        super(NoBlobsFound, self).__init__(message)

        self.errors = errors
