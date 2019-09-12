"""
Nameko dispatch(RPC etc) Wrapper Module
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from nameko.standalone.rpc import ClusterRpcProxy


class RpcMixin(object):
    """RPC 调用混入

    用于 View类视图 混入，包装rpc调用逻辑
    """
    service_name = None     # 服务名

    try:
        _rpc_config = settings.NAMEKO['AMQP']  # RPC config
    except AttributeError:
        assert False, ImproperlyConfigured("""
        Nameko settings don't in settings file, please set `NAMEKO` settings in settings.
        Format:
            NAMEKO: {
                'AMQP': {
                    'AMQP_URI': 'amqp://username:password@host:port'
                }
            }
        """)

    # ************************ Attach RPC params ************************
    def get_rpc_params(self):
        """获取Rpc参数"""
        return getattr(self, '_rpc_params', {})

    def set_rpc_params(self, value):
        """设置Rpc参数"""
        if not isinstance(value, dict):
            raise ValueError('`value` type must be dict')
        else:
            if getattr(self, '_rpc_params', {}):
                self._rpc_params.update(value)
            else:
                self._rpc_params = value

    rpc_params = property(get_rpc_params, set_rpc_params)

    def rpc(self, service_name, service_method):
        """RPC 调用

        Args:
            service_name: 服务名（对应nameko微服务name名）
            service_method: 服务RPC方法（nameko微服务rpc装饰方法）

        Returns:
            RPC调用结果
        """

        def wrapper(*args, **kwargs):
            with ClusterRpcProxy(self._rpc_config) as cluster_rpc:
                service = getattr(cluster_rpc, service_name)    # 此处异常`AttributeError`正常抛出
                # kwargs 添加`params`参数，kwargs参数优先级高于`params`优先级
                # 添加分页自动处理
                if self.rpc_params:
                    kwargs = dict(self.rpc_params, **kwargs)
                print('RPC dispatch kwargs:', kwargs, self.rpc_params)
                return getattr(service, service_method)(*args, **kwargs)
        return wrapper

