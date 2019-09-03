# encoding:utf-8
"""
此处使用 keijack/python-eureka-client 作为与eureka对接的单元
也可以使用Spring自带的sidecar
感谢keijack的项目
项目仓库:
https://gitee.com/keijack/python-eureka-client.git
"""
from dophon import cloud_client_properties as properties
from dophon_logger import *
from ..utils import get_host_ip

name = "eureka_client"

get_logger(DOPHON).inject_logger(globals())
from .eureka_client import *
# from .eureka_client_urllib3 import *

assert properties.client, '无法获取client配置,请检查配置文件'

client_config = properties.client

app_name = client_config.name if hasattr(client_config, 'name') else __name__
ins_host = client_config.host if hasattr(client_config, 'host') else get_host_ip()  # properties.host
ins_ip = (client_config.ip if hasattr(client_config, 'ip') else get_host_ip()) \
    if client_config.prefer_ip else 'localhost'  # properties.ip
ins_port = client_config.port if hasattr(client_config, 'port') else properties.port
ha_type = eval(client_config.ha if hasattr(client_config, 'ha') else 'HA_STRATEGY_RANDOM')

# 断言校验
assert app_name and isinstance(app_name, str), 'app_name参数不正确,请检查参数'
assert ins_host and isinstance(ins_host, str), 'ins_host参数不正确,请检查参数'
assert ins_ip and isinstance(ins_ip, str), 'ins_ip参数不正确,请检查参数'
assert ins_port and isinstance(ins_port, int) and ins_port >= 0, 'ins_port参数不正确,请检查参数'
assert ins_port == properties.port, f'实例监听端口异常{ins_port} -- {properties.port}'

logger.info(f'初始化服务单元{client_config}')
# 启动eureka_client单元
# The flowing code will register your server to eureka server and also start to send heartbeat every 30 seconds
client_proxy, discovery_proxy = init(eureka_server=client_config.center,
                                                   app_name=app_name,
                                                   # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                                                   instance_host=ins_host,
                                                   instance_port=ins_port,
                                                   instance_ip=ins_ip,
                                                   # 调用其他服务时的高可用策略，可选，默认为随机
                                                   ha_strategy=ha_type)

logger.info(f'服务单元初始化完毕')

from dophon import boot
from dophon.annotation import *

bean(name='discovery_proxy')(lambda: discovery_proxy)()


def open_cloud(f, *args, **kwargs):
    @boot.BeanScan()
    def inner_method():
        try:
            f(boot=boot, *args, **kwargs)
        except:
            f(*args, **kwargs)
        stop()
        return

    return inner_method


OpenCloud = open_cloud

__all__ = ['OpenCloud']
