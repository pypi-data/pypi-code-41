class Response(object):
    """
    Base Response object
    """

    def __init__(self):
        """Initializes Response"""

        self.message = ""
        self.errors = list()
        self.success = False
        self.data = dict()

    def get_response(self):
        """Returns response as a dict"""
        return dict(
            success=self.success,
            errors=self.errors,
            data=self.data,
            message=self.message
        )