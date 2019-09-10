"""
Decorator Module
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def page(size=None):
    """
    列表视图分页装饰器
    如果视图函数被此装饰装饰，则表示此视图为分页视图，size的值依次由URL查询参数size、自定义size，默认size依次决定，
    offset则由URL offset参数或默认值（0）决定。
    Args:
        size: 分页大小

    Returns:
        列表
    """
    # 参数检查
    if 'PAGINATION' in settings.NAMEKO and 'SIZE' in settings.NAMEKO['PAGINATION']:
        PAGINATION_DEFAULT_SIZE = settings.NAMEKO['PAGINATION']['SIZE']  # 默认分页大小
    else:
        raise ImproperlyConfigured(
            '''Django settings `NAMEKO` need include `PAGINATION` setting and include `SIZE` in `PAGINATION`.'''
        )
    size = PAGINATION_DEFAULT_SIZE if not size else size

    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            nonlocal size
            if 'size' in request.GET and request.GET['size'].isnumeric():
                if int(request.GET['size']) > 0:
                    size = int(request.GET['size'])

            if 'offset' in request.GET and request.GET['offset'].isnumeric():
                offset = int(request.GET['offset'])     # >=0
            else:
                offset = 0

            request_get_copy = request.GET.copy()   # request.GET 对象为不可变对象
            request_get_copy['offset'] = offset + size
            next_url = request.build_absolute_uri(request.path) + '?' + request_get_copy.urlencode()
            if offset == 0:
                prev_url = None
            else:
                request_get_copy['offset'] = offset - size
                if request_get_copy['offset'] < 0:
                    request_get_copy['offset'] = 0
                prev_url = request.build_absolute_uri(request.path) + '?' + request_get_copy.urlencode()

            request.pagination = {'size': size, 'offset': offset, 'prev': prev_url, 'next': next_url}
            print(request.pagination)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

