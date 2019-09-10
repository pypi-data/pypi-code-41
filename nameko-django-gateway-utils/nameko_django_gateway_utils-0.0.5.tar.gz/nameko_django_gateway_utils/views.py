import json
import importlib

from django.views import View
from django.http.request import QueryDict
from django.conf import settings

from .mixins.dispatch import RpcMixin
from .exceptions import NotAllowedMethod, NeedAuthentication, PermissionDenied, ViewErrorException
from .libs.import_tools import import_object_from_path
from .requests import request_params_to_dict


class RpcView(View, RpcMixin):
    """具有RPC调用方法的视图类"""
    # auth_required = False       # 视图需要认证控制参数
    permission_classes = []     # 权限类
    pagination_class = None     # 分页类
    pagination_info = None        # 分页信息
    paginator = None            # 分页器

    # ************************ Request Header Support ************************
    def add_json_header_support(self, request):
        # 增加request请求头对`application/json`的支持 （request是可变对象）
        if request.META['CONTENT_TYPE'].find('application/json') != -1 and request.method == 'POST':
            query_dict = self._request_body_parse(request)
            if query_dict:
                setattr(request, request.method.upper(), query_dict)

    @staticmethod
    def _request_body_parse(request):
        """request body parse"""
        print(request.method, request.META['CONTENT_TYPE'], request.body, QueryDict(request.body))
        print('Request Body:', request.body)
        if request.META['CONTENT_TYPE'].find('application/json') != -1:
            try:
                request_body_dict = json.loads(request.body)
            except json.decoder.JSONDecodeError:
                return None
            else:
                query_dict = QueryDict(mutable=True)
                for item, value in request_body_dict.items():
                    query_dict[item] = value
                return query_dict
        elif request.META['CONTENT_TYPE'].lower() == 'application/x-www-form-urlencoded':
            return QueryDict(request.body, mutable=True)
        else:
            raise ViewErrorException(
                'Request body parse: UnSupport form format: {}'.format(request.META['CONTENT_TYPE'].lower())
            )

    # ************************ Request Params ************************
    def get_request_params(self, *, all_params_names=None, list_params_names=None, value_params_names=None, **kwargs):
        """获取请求参数

        当使用分页器时应当使用此方法获取请求参数，此方法会移除分页器参数，返回其它以外参数
        """
        params_dict = request_params_to_dict(self.request.GET, all_params_names, list_params_names, value_params_names)
        result = {}
        for key in params_dict.keys():
            if not (type(key) is str and key.lower() in ['size', 'offset']):
                result[key] = params_dict[key]
        return result

    # ************************ Permission Support ************************
    @staticmethod
    def get_default_permission_classes():
        """获取默认权限"""
        permission_classes = [
            import_object_from_path(path) for path in getattr(settings, 'NAMEKO')['DEFAULT_PERMISSION_CLASSES']
        ]
        return permission_classes

    def get_permission_classes(self):
        """获取权限类"""
        if getattr(self, 'permission_classes', None):
            # 使用默认权限类
            permission_classes = self.permission_classes
        else:
            # 使用视图权限
            permission_classes = self.get_default_permission_classes()
        return permission_classes

    def check_permissions(self, request):
        """检查当前请求权限

        Returns:
            True, True when pass else raise Exception

        Raises:
            PermissionDenied
        """
        permission_classes = self.get_permission_classes()
        result = all(map(lambda cls: cls().has_permission(request, self), permission_classes))
        print('check permissions result:', permission_classes, result)
        if result:
            return result
        else:
            raise PermissionDenied

    # ************************ Request Payload ************************
    def get_payload(self, request, *, include_user=False):
        """获取向微服务发送数据内容

        Args:
            include_user: bool/string 是否包含用户信息，当参数为字符串时，将字符串作为字典键

        Raises:
            NeedAuthentication: 当request.user不存在时，引发认证异常，此异常由中间件处理
        """
        ALLOW_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')
        DEFAULT_USER_KEY = 'user_id'

        print('Get payload', request.method)
        if request.method in ALLOW_METHODS:
            # request.`method`方法返回的为QueryDict对象将其转换为字典
            if request.method == 'POST':
                payload = getattr(request, request.method, QueryDict()).dict()
            else:
                parse_result = self._request_body_parse(request)
                if parse_result:
                    payload = self._request_body_parse(request).dict()
                else:
                    payload = dict()

            if include_user:
                if request.user:
                    user_key = include_user if type(include_user) is str else DEFAULT_USER_KEY
                    payload[user_key] = request.user.id
                else:
                    raise NeedAuthentication

            return payload
        else:
            raise NotAllowedMethod("Request `{}` method doesn't allow to use this method".format(request.method))

    # ************************ Pagination Support ************************
    def get_pagination_info(self, request):
        """获取分页信息

        此处动态添加类属性`paginator`和`rpc_params`
        """
        if self.pagination_class and request.method == 'GET':
            # 初始化分页器，并获取分页请求参数
            self.paginator = self.pagination_class(request)
            self.rpc_params = {'page': self.paginator.get_pagination_params()}
        else:
            self.paginator = None
            self.rpc_params = {}

    def paging(self, rpc_result):
        if getattr(self, 'paginator', None):
            return self.paginator.paging(result=rpc_result)
        else:
            raise ViewErrorException('Before you use paging method, you must set `pagination_class`.')

    # View function dispatch
    def dispatch(self, request, *args, **kwargs):
        """对`View`视图调用进行包装处理"""
        # 检查权限
        self.check_permissions(request)

        # 增加request请求头对`application/json`的支持
        self.add_json_header_support(request)

        # 添加分页支持，获取分页参数
        self.get_pagination_info(request)
        print('rpc params:', self.rpc_params)
        # print(request.method, getattr(self, request.method.lower()))

        return super().dispatch(request, *args, **kwargs)

    def is_json_request(self):
        if self.request.META['CONTENT_TYPE'].find('application/json') == -1:
            return False
        else:
            return True

