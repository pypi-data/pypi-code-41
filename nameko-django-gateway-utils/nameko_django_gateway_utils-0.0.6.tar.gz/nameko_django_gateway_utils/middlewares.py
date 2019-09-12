from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http.response import JsonResponse

from .exceptions import ViewException
from .auth import UserObject


SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME
USER_SESSION_NAME = settings.NAMEKO['SESSION']['USER_NAME']


class AuthenticationBaseMiddleWare(MiddlewareMixin):

    """
    Authentication MiddleWare

    对request对象添加`UserObject`属性
    """
    pass


class AuthenticationMiddleWare(AuthenticationBaseMiddleWare):
    """
    Authentication MiddleWare
    """

    def process_request(self, request):
        """利用session读取的Cookie信息获取用户对象，并将用户对象赋给`request.user`"""

        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")

        if request.session and USER_SESSION_NAME in request.session:
            # 从session获取对应id的用户信息
            request.user = UserObject(request.session[USER_SESSION_NAME])
        else:
            request.user = UserObject(None)


class WeChatAuthenticationMiddleware(AuthenticationMiddleWare):
    """WeChat 认证中间件"""
    pass


class HandleViewExceptionMiddleware(MiddlewareMixin):
    """视图异常处理"""

    def process_exception(self, request, exception):
        if isinstance(exception, ViewException):
            msg = getattr(exception, 'msg', '无效的请求！')
            code = getattr(exception, 'code', 400)

            return JsonResponse(data={'info': msg}, status=code)
