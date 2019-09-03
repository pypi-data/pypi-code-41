# coding: utf-8
import random
from flask import Flask, jsonify, request as reqq
from urllib import request, parse
import socket, hashlib, re, time, threading
import urllib3
import urllib3.util
from dophon_logger import *
from dophon import properties
from .decrate_enhance import e_app,e_dophon

get_logger(DOPHON).inject_logger(globals())


class micro_cell():
    '''
    远程请求调用封装类,用urllib处理请求发送和响应处理
    '''
    # 暂时启用轮询方式访问实例
    __instance_index = 0

    def __init__(self, e_app, service_name: str, interface: str, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None):

        self.__interface = interface
        self.__service_name = service_name.upper()
        self.__interface_app = e_app
        info = e_app.reg_info()
        # 启动远程调用部件初始化线程
        threading.Thread(target=self.listen_instance, kwargs={
            'info': info,
            'init_args': {
                'data': data,
                'headers': headers,
                'origin_req_host': origin_req_host,
                'unverifiable': unverifiable,
                'method': method
            },
            'debug_trace': getattr(properties, 'cloud_debug_trace', False)
        }).start()

    def listen_instance(self, info: dict, init_args: dict, debug_trace: bool):
        """
        防止远程调用部件加载失败导致服务瘫痪
        :param info:
        :return:
        """
        retry = 0
        while True:
            if self.__service_name in info:
                # 获取服务对应的实例列表
                self.__instances = info[self.__service_name]
                logger.info('服务(' + self.__service_name + ')远程调用建立')
                break
            else:
                # 服务不存在请求注册中心获得服务实例信息
                self.__interface_app.async_reg_info()
                # 再次检查服务信息
                if self.__service_name in self.__interface_app.reg_info():
                    self.__instances = self.__interface_app.reg_info()[self.__service_name]
                    logger.info('服务(' + self.__service_name + ')远程调用建立(重请求)')
                    break
                else:
                    if debug_trace and retry < 3:
                        # 提示三次后关闭提示
                        logger.warning('服务(' + self.__service_name + ')不存在!,远程调用有丢失风险')
                        retry += 1
            # 阻塞等待服务启动
            time.sleep(2)
        instance = self.__instances[self.__instance_index]
        # 检查服务注册信息(防止调用自身)
        if self.__interface_app.service_name() == self.__service_name:
            print('警告::使用有风险的远程调用单元(', self.__service_name, ',', self.__interface, '),可能导致请求失败')
            try:
                if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                        and \
                        instance['port'] is self.__interface_app.port():
                    # 检查请求路径
                    self.__instances.pop()
                instance = self.__instances[self.__instance_index]
            except Exception as e:
                raise e
        url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
        self.__id = instance['id']
        self.__req_obj = request.Request(url=url, **init_args)

    def check_active(self):
        try:
            self.__req_obj
        except:
            return False
        else:
            return True

    def __str__(self):
        return hashlib.sha1(
            (re.sub(':', '', self.__host) + str(self.__interface)).encode('utf8')).hexdigest()

    def __eq__(self, other):
        return str(other) == self.__str__()

    def request(self, data=None):
        '''
        发起远程请求
        :param data: 请求数据
        :return: 请求响应
        '''
        pass
        # 重写数据集(无数据集调用初始化数据集)
        _data = data if data else self.__req_obj.data
        if hasattr(self, '__instances'):
            instance = self.__instances[self.__instance_index]
            # 检查服务注册信息(防止调用自身)
            if self.__interface_app.service_name() == self.__service_name:
                print('警告::(有风险)使用远程调用单元调用自身服务(', self.__service_name, ',', self.__interface, '),可能导致请求失败')
                try:
                    if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                            and \
                            instance['port'] is self.__interface_app.port():
                        # 检查请求路径
                        self.__instances.pop()
                    else:
                        self.__instance_index = self.__instance_index + 1
                    instance = self.__instances[self.__instance_index]
                    url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
                    setattr(self.__req_obj, 'full_url', url)
                except Exception as e:
                    # print(e)
                    pass
            res = request.urlopen(self.__req_obj,
                                  data=bytes(parse.urlencode(_data), encoding="utf8") if _data else None)
            # 轮询方式访问实例
            self.__instance_index = (self.__instance_index + 1) if self.__instance_index < len(
                self.__instances) - 2 else 0
            self.__id = instance['id']
            url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
            setattr(self.__req_obj, 'full_url', url)
            # 处理结果集
            remote_result = res.data.decode('utf8')
            try:
                remote_result = eval(remote_result)
            except SyntaxError as se:
                remote_result_list = re.sub('(<\w+>|</\w+>)', '\n', remote_result).split('\n')
                remote_result = ' '.join(remote_result_list)
            return remote_result
        else:
            return {'event': 404, 'msg': self.__service_name + '服务调用异常'}

    def pool_request(self, pool: urllib3.PoolManager, data: dict = None):
        """
        池化http请求方式发起远程调用
        :param pool: urllib3连接池实例
        :param data:请求参数
        :return:
        """
        try:
            # 轮询方式访问实例
            instance = self.__instances[self.__instance_index]
            # 检查服务注册信息(防止调用自身)
            if self.__interface_app.service_name() == self.__service_name:
                print('警告::(有风险)使用远程调用单元调用自身服务(', self.__service_name, ',', self.__interface, '),可能导致请求失败')
                try:
                    if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                            and \
                            instance['port'] is self.__interface_app.port():
                        # 检查请求路径
                        self.__instances.pop()
                    else:
                        self.__instance_index = self.__instance_index + 1
                    instance = self.__instances[self.__instance_index]
                except Exception as e:
                    # print(e)
                    pass
            url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
            res = pool.request(method=self.__req_obj.get_method(), url=url, fields=data)
            self.__id = instance['id']
            self.__instance_index = (self.__instance_index + 1) if self.__instance_index < len(
                self.__instances) - 2 else 0
            url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
            setattr(self.__req_obj, 'full_url', url)
            remote_result = res.data.decode('utf8')
            try:
                remote_result = eval(remote_result)
            except SyntaxError as se:
                remote_result_list = re.sub('(<\w+>|</\w+>)', '\n', remote_result).split('\n')
                remote_result = ' '.join(remote_result_list)
            return remote_result if res.status == 200 else {'event': res.status,
                                                            'msg': self.__service_name + '服务调用异常'}
        except Exception as e:
            return {'event': 500, 'msg': self.__service_name + '服务调用异常', 'reason': str(e)}


class micro_cell_list():
    '''
    服务调用集合类,自带urllib3连接池
    '''
    __family = {}

    def __init__(self, app, pool_size: int = 10, properties: dict = {}):
        '''
        初始化远程调用实例集群

        连接池默认连接数为10

        配置格式:{
            service_name<str> :[
                {
                    public_interface_prefix_1<str>:[
                            interface_prefix_1<str>,
                            interface_prefix_2<str>,
                            ...
                        ]
                },
                {
                    public_interface_prefix_2<str>:[
                            interface_prefix_1<str>,
                            interface_prefix_2<str>,
                            ...
                        ]
                },
                    ...
                ]
        }

        初始化后集群格式:
            {
                service_name<str>:
                    {
                        public_interface_prefix_1<str>:{
                                interface_prefix_1<str>:<micro_cell>,
                                interface_prefix_2<str>:<micro_cell>,
                                interface_prefix_3<str>:<micro_cell>,
                                ...
                        },
                        public_interface_prefix_1<str>:{
                                interface_prefix_1<str>:<micro_cell>,
                                interface_prefix_2<str>:<micro_cell>,
                                interface_prefix_3<str>:<micro_cell>,...
                        }
                    },...
            },...
        '''
        act_pool_workers = pool_size
        # 根据配置初始化集群
        if properties:
            # 存在集群配置
            for k, v in properties.items():
                services = {}
                for pub_v_item in v:
                    public_interfaces = {}
                    for k_item in pub_v_item:
                        if not str(k_item).startswith('/'):
                            raise Exception('配置路径格式有误,请以/开头(service_name:' + k + ',public_prefix:' + k_item + ')')
                        v_item = pub_v_item[k_item]
                        interface = {}
                        for item in v_item:
                            if not str(item).startswith('/'):
                                raise Exception(
                                    '配置路径格式有误,请以/开头(service_name:' + k + ',public_prefix:' + k_item + ',prefix:' + item + ')')
                            # 实例化远程调用实例
                            m_cell = micro_cell(app, str(k), str(k_item) + str(item))
                            interface[item] = m_cell
                            act_pool_workers += 1
                        public_interfaces = interface
                    services[k_item] = public_interfaces
                self.__family[k.upper()] = services
        # 初始化连接池
        self.__req_pool = urllib3.PoolManager(act_pool_workers)

    def request(self, service_name: str, interface: list, data: dict = None):
        """
        直接使用配置的服务调用单元集群发起请求
        使用多线程发起请求
        :param service_name: 服务名
        :param interface: 接口名,格式[公用接口,细化接口]
        :return:
        """
        try:
            _pub_interface_prefix = interface[0]
        except Exception:
            # 无法取值则默认为空
            _pub_interface_prefix = ''
        try:
            _interface_prefix = interface[1]
        except Exception:
            # 无法取值则默认为空
            _interface_prefix = ''
        args = (service_name.upper(), _pub_interface_prefix, _interface_prefix, self.__req_pool, data)
        try:
            service_cell = self.__family[service_name.upper()][_pub_interface_prefix][_interface_prefix]
            target_obj = lambda service_name, __pb_inter_pre, __inter_pre, pool, data=None: \
                service_cell.pool_request(pool=pool, data=data)
            result = target_obj(*args)
            return result if service_cell.check_active() else {
                'event': 404,
                'msg': '实例不存在',
                'service_name': service_name
            }

        except KeyError as ke:
            raise Exception('接口映射未定义: %s ' % ke)

    def get_cell_obj(self, service_name: str, interface: list):
        """
        获取对应服务调用单元实例<micro_cell>
        :param service_name: 服务名
        :param interface: 接口名,格式[公用接口,细化接口]
        :return:
        """
        _pub_prefix = interface[0] if interface[0] else ''
        _prefix = interface[1] if len(interface) > 1 and interface[1] else ''
        return self.__family[service_name][_pub_prefix][_prefix]

def enhance(import_name, properties: dict, static_url_path=None,
            static_folder='static', template_folder='templates',
            instance_path=None, instance_relative_config=False,
            root_path=None):
    '''
    获取增强服务器实例方法
    :param import_name: 实例代号,通常为__name__
    :param properties: 增强配置对象,类型为json
    :param static_path:
    :param static_url_path:
    :param static_folder:
    :param template_folder:
    :param instance_path:
    :param instance_relative_config:
    :param root_path:
    :return:增强服务器实例(可作为微服务)
    '''
    obj = e_app(import_name, properties, static_url_path=static_url_path,
                static_folder=static_folder, template_folder=template_folder,
                instance_path=instance_path, instance_relative_config=instance_relative_config,
                root_path=root_path)
    return obj


def instance_not_exist():
    """
    实例不存在的共用方法
    :return:
    """
    return {'event': 404, 'msg': '实例不存在'}
