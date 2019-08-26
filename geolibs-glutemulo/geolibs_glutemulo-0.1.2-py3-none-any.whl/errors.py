class Error(Exception):
    """Generic error"""

    def __init__(self, message):
        self.message = message
        super(Error, self).__init__(message)

    def __repr__(self):
        return "{klass}(error={error})".format(
            klass=self.__class__.__name__, error=self.message
        )

    def __str__(self):
        return self.message


class ProducerError(Error):
    pass


class TopicError(Error):
    pass


class SerializerError(Error):
    pass


class ValidationError(SerializerError):
    pass
