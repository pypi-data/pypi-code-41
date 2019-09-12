"""
MicroService Paginator
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class PaginatorBase(object):
    """
    Result Pagination
    """
    size = None

    def __init__(self, request, *, size=None, offset=None):
        """
        初始化分页器（请求、结果、设置）

        请求request对象中的`size`和`offset`会覆盖默认设置
        Args:
            request: HTTP Request对象
            result: 微服务返回结果对象
        """
        self.request = request

        # 读取全局分页器设置
        # size
        if not self.get_pagination_size():
            if size is None:
                if not getattr(self, 'size', None):
                    print('self.size = none')
                    if 'PAGINATION' in settings.NAMEKO and 'SIZE' in settings.NAMEKO['PAGINATION']:
                        self.size = settings.NAMEKO['PAGINATION']['SIZE']     # 默认分页大小
                    else:
                        raise ImproperlyConfigured(
                            'Django settings `NAMEKO` need include `PAGINATION` setting and'
                            ' include `SIZE` in `PAGINATION`.'
                        )
            else:
                self.size = size
        # offset
        self.offset = self.get_pagination_offset(offset)

    def get_pagination_size(self):
        """获取请求URL中分页大小"""
        if 'size' in self.request.GET and self.request.GET['size'].isnumeric():
            if int(self.request.GET['size']) > 0:
                self.size = int(self.request.GET['size'])
                return self.size
        return None

    def get_pagination_offset(self, offset):
        """获取请求URL中分页偏移值"""
        if 'offset' in self.request.GET and self.request.GET['offset'].isnumeric():
            return int(self.request.GET['offset'])  # >=0
        else:
            if offset is None or offset < 0:
                return 0
            else:
                return offset

    def get_pagination_info(self, result):
        """获取分页URL信息"""

        request_get_copy = self.request.GET.copy()  # request.GET 对象为不可变对象
        # Next URL
        # print('DFJIDJFISAFJAs', result)
        search_result = result['data']['result'] if result['data'] and 'result' in result['data'] else []
        if type(search_result) is list:
            if len(search_result) == self.size:
                request_get_copy['offset'] = self.offset + self.size
                next_url = self.request.build_absolute_uri(self.request.path) + '?' + request_get_copy.urlencode()
            else:
                request_get_copy['offset'] = self.offset + len(search_result)
                next_url = None
        else:
            next_url = None

        # Prev URL
        if self.offset == 0:
            prev_url = None
        else:
            request_get_copy['offset'] = self.offset - self.size
            if request_get_copy['offset'] < 0:
                request_get_copy['offset'] = 0
            prev_url = self.request.build_absolute_uri(self.request.path) + '?' + request_get_copy.urlencode()

        pagination = {'size': self.size, 'offset': self.offset, 'prev': prev_url, 'next': next_url}
        print(pagination)
        return pagination

    def get_pagination_params(self):
        """获取分页参数，用于分页服务请求"""
        return {'size': self.size, 'offset': self.offset}

    def paging(self, result):
        """进行分页"""
        pagination_info = self.get_pagination_info(result)
        result['next'] = pagination_info['next']
        result['prev'] = pagination_info['prev']

        # print('Paging Result:', result)
        return result


class RpcPaginator(PaginatorBase):
    """Rpc 结果分页器"""
    size = 7


# class RpcPaginator(PaginatorBase):
#     """RPC 调用结果分页器"""
#
#     def __init__(self, request, rpc_func, *args, **kwargs):
#         self.rpc_func = rpc_func
#         super().__init__(request, *args, **kwargs)
#
#     def rpc_call(self, *args, **kwargs):
#         """RPC 调用"""
#         rpc_result = self.rpc_func(page=self.get_pagination_params(), *args, **kwargs)
#         return self.paging(rpc_result)


class SmallPaginator(PaginatorBase):
    """RPC Small 分页器"""
    size = 10


class MediumPaginator(PaginatorBase):
    """RPC Medium 分页器"""
    size = 30