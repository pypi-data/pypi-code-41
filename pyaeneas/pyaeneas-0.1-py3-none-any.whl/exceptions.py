class AeneasError(Exception):
    """ Aeneas base exception """

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class AeneasResponseError(AeneasError):
    def __init__(self, text: str, sql_code: str):
        self.text = text
        self.sql_code = sql_code

    def __str__(self):
        return str(self.__dict__)


class AeneasConnectionError(AeneasError):
    pass


class AeneasActionError(AeneasError):
    pass
