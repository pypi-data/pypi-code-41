class BaseAPIError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class CodeError(BaseAPIError):
    code = None

    def __init__(self, errors):
        self.errors = errors
        super().__init__(f'code: {self.code}, ' + str(errors))


class AuthorizationError(CodeError):
    code = 100


class MethodNotExistError(CodeError):
    code = 101


class ClientError(CodeError):
    code = 102


class EAISTOError(CodeError):
    code = 103


class ActionNotAllowedError(CodeError):
    code = 202


class UnknownError(CodeError):
    code = 200


class UnexpectedError(CodeError):
    def __init__(self, code, errors):
        self.code = code
        super().__init__(errors)


class MultiError(BaseAPIError):
    def __init__(self, error_list):
        self.error_list = error_list
        code_list = (error.code for error in self.error_list)
        super().__init__('Error codes: {}'.format(', '.join(map(str, code_list))))
