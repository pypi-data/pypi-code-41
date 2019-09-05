class TelegraphException(Exception):
    pass


class TelegraphRequestException(TelegraphException):
    def __init__(self, error: str, method: str, **params):
        super().__init__("Get error %s" % error)
        self.error = error
        self.method = method
        self.params = params


class TelegraphTokenException(TelegraphException):
    def __init__(self):
        super().__init__("Need access_token")
