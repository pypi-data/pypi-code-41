"""
Custom Exception
"""


class ViewException(Exception):
    """视图异常 --- 此异常可通过中间件捕捉"""
    msg = 'View Exception'
    code = 400

    def __init__(self, msg=None, code=None):
        self.msg = msg if msg else self.msg
        self.code = code if code else self.code

    def __str__(self):
        return self.msg


class ViewErrorException(Exception):
    """视图错误异常 --- 此异常直接抛出"""
    pass


class NotAllowHeader(ViewException):
    """请求头错误"""
    msg = '不允许的请求头'
    code = 400


class NotAllowedMethod(ViewErrorException):
    """不允许的方法"""
    pass


class NeedAuthentication(ViewException):
    """需要认证"""
    msg = '需要认证'
    code = 401


class PermissionDenied(ViewException):
    """权限拒绝"""
    msg = '不允许的操作'
    code = 403

