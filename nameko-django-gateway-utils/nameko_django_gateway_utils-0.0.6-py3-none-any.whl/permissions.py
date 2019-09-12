"""
视图权限管理 --- 参考`Django Restful` API框架设计
"""
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class BasePermission(object):
    """权限基类"""

    def has_permission(self, request, view):
        """根据请求判断权限"""
        pass


class AllowAny(BasePermission):
    """允许任何访问"""

    def has_permission(self, request, view):
        return True


class Authenticated(BasePermission):
    """仅允许认证用户"""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class AuthenticatedOrReadonly(BasePermission):
    """允许认证用户或其它用户仅可读"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated


class IsAdmin(BasePermission):
    """管理员权限"""

    def has_permission(self, request, view):
        return getattr(request.user, 'is_admin', False)


class IsAdminOrReadonly(BasePermission):
    """管理员权限或仅可读"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            try:
                return request.user.is_admin
            except KeyError:
                return False
