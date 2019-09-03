import re
import socket
import threading
import time
from flask import request as reqq, jsonify, Flask
import urllib3
import random
from dophon_logger import *

get_logger(DOPHON).inject_logger(globals())


class e_app(Flask):
    '''

    服务器封装类(不支持dophon)


    请求的发送和封装使用urllib3处理
    简单的一个基于flask服务器的一个实例
    '''

    __host = '127.0.0.1'
    __port = 5000
    __reg_url = 'http://localhost:8361/reg/service/'
    __reg_update_url = None
    __reg_info = {}
    __reg_heart = False
    __reg_center_list = []
    # 建立池化连接池
    __req_pool_pool = {}

    '''
    增强app内部定义连接池(默认10个连接数)
    '''
    req_pool = urllib3.PoolManager()

    def __init__(self, import_name, properties: dict, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False,
                 root_path=None):
        '''
        初始化服务器实例
        :param import_name:
        :param properties:
        :param static_url_path:
        :param static_folder:
        :param static_host:
        :param host_matching:
        :param subdomain_matching:
        :param template_folder:
        :param instance_path:
        :param instance_relative_config:
        :param root_path:
        '''
        # 启动微服务注册参数预处理流程
        if type(properties) is type(''):
            # 反射获取配置
            try:
                prop = __import__(properties)
                self.__prop = {
                    'host': getattr(prop, 'host', self.__host),
                    'port': getattr(prop, 'port', self.__port),
                    'service_name': getattr(prop, 'service_name').upper(),
                    'health_interface': getattr(prop, 'health_interface', '/heart'),
                    'prefer_own_ip': getattr(prop, 'prefer_own_ip', False)
                }
            except Exception as e:
                raise Exception('配置文件加载失败,请检查路径,错误信息:(' + str(e) + ')')
        elif isinstance(properties, type(())):
            raise Exception('暂不支持元组类型配置,请选择其他配置')
        elif isinstance(properties, type({})):
            if 'service_name' in properties.keys():
                self.__prop = {
                    'service_name': properties['service_name'].upper(),
                    'health_interface': properties[
                        'health_interface'] if 'health_interface' in properties.keys() else '/heart',
                    'host': properties['host'] if 'host' in properties.keys() else self.__host,
                    'port': properties['port'] if 'port' in properties.keys() and isinstance(properties['port'],
                                                                                             type(1)) else self.__port,
                    'prefer_own_ip': socket.gethostbyname(
                        socket.getfqdn(socket.gethostname())) if 'prefer_own_ip' in properties.keys() and isinstance(
                        properties['prefer_own_ip'], type(True)) else False
                }
            else:
                raise Exception('缺少必要参数(service_name)')
        # 初始化服务器
        Flask.__init__(self, import_name, static_url_path=static_url_path,
                       static_folder=static_folder, template_folder=template_folder,
                       instance_path=instance_path, instance_relative_config=instance_relative_config,
                       root_path=root_path)
        print('实例注册参数::', self.__prop)
        self.init_reg_url(properties)
        self.regist_myself()
        # 注册自身功能接口
        self.add_url_rule('/heart/as/<service_name>', 'receive_heart', self.receive_heart, methods=['POST'])
        self.add_url_rule('/heart', 'show_own_info', self.show_own_info, methods=['POST'])

    def init_reg_url(self, properties: dict):
        """
        初始化注册信息
        :param properties:
        :return:
        """
        self.__reg_url = (properties['reg_url'] if 'reg_url' in properties.keys() else self.__reg_url) + self.__prop[
            'service_name']
        self.init_reg_update_url()

    def init_reg_update_url(self):
        """
        初始化注册信息更新接口
        :return:
        """
        self.__reg_update_url = re.sub('/reg/service/.*', '/reg/update', self.__reg_url)

    def regist_myself(self):
        """
        向注册中心注册自身服务
        :return:
        """
        while True:
            try:
                # 向注册中心发起注册
                res = self.req_pool.request(method='get', url=self.__reg_url, headers={
                    'prefer_ip': socket.gethostbyname(socket.getfqdn(socket.gethostname())) if self.__prop[
                        'prefer_own_ip'] else self.__host,
                    'service_port': self.__prop['port']
                })
                res_data = eval(res.data.decode('utf8'))
                if 'DOPHON_REG_CENTER_CLUSTERS' in res_data:
                    _cache_reg_center_list = res_data.pop('DOPHON_REG_CENTER_CLUSTERS')
                    _cache_list = []
                    for val in _cache_reg_center_list.values():
                        _cache_list.append(
                            'http://' + val['host'] + ':' + str(val['port']) + '/reg/service/' + self.__prop[
                                'service_name']
                        )
                    self.__reg_center_list = _cache_list
                self.__reg_list_info = res_data
                break
            except Exception as e:
                print('微服务(%s)启动失败!!,错误原因:: %s' % (self.__prop['service_name'].upper(), str(e)))
                if self.__reg_center_list:
                    print('存在注册中心集群,正在从备选中重新注册')
                    # 将当前注册路径放入备选列表
                    self.__reg_center_list.append(self.__reg_url)
                    # 在备选列表中挑选一个注册中心进行注册(默认fifo)
                    trys_url = self.__reg_center_list.pop(random.randint(0, len(self.__reg_center_list) - 1))
                    print('原注册路径:', self.__reg_url, '\n', '备选注册路径:', trys_url, '\n', '备选列表:', self.__reg_center_list)
                    self.__reg_url = trys_url
                    self.init_reg_update_url()
                print('30秒后重新注册')
                time.sleep(30)

    def service_name(self):
        return self.__prop['service_name']

    def port(self):
        return self.__prop['port']

    '''
    运行增强服务器
    '''

    def run(self, host=None, port=None, debug=None, **options):
        # 启动注册中心健康监测
        threading.Thread(target=self.check_reg_center).start()
        self.config['JSON_AS_ASCII'] = False
        # 初始化注册服务实例(根据注册时返回的实例信息)
        Flask.run(self,
                  host=self.__prop['host'],
                  port=self.__prop['port'],
                  )

    def update_reg_info(self, r):
        """
         更新微服务集群信息
        :param r:
        :return:
        """
        if not isinstance(r, type({})):
            for k in r.keys():
                v = r[k]
                r[k] = eval(v)
        if hash(str(self.__reg_info)) != hash(str(r)):
            logger.info('更新实例注册信息, %s %s' % (str(r), type(r)))
            self.__reg_info = r
        # 写入接收心跳标识
        if not self.__reg_heart:
            self.__reg_heart = True

    '''
    获取注册中心服务注册信息
    '''

    def reg_info(self):
        return self.__reg_info if self.__reg_info else self.__reg_list_info

    '''
    同步服务信息
    '''

    def async_reg_info(self):
        if not self.__req_pool_pool:
            addr = self.__reg_url.split('//')[1].split('/')[0].split(':')
            self.__req_pool_pool = urllib3.HTTPConnectionPool(addr[0], int(addr[1]), maxsize=10, block=False, retries=3,
                                                              timeout=urllib3.util.Timeout.DEFAULT_TIMEOUT)
        try:
            # 暂时使用重注册更新服务信息
            res = self.__req_pool_pool.request(method='get', url=self.__reg_update_url)
            result = eval(res.data.decode('utf8'))
            self.__reg_info = result
            return result
        except:
            return {}

    def check_reg_center(self):
        if self.__reg_heart:
            # 存在接收心跳标识
            return
        else:
            # 定期检查注册中心
            while True:
                # 五分钟检查一次(默认)
                time.sleep(300)
                try:
                    res = self.req_pool.request(url=re.sub('/reg/service/.*', '/health', self.__reg_url), method='GET')
                    print('注册中心存活' if res.status == 200 else '注册中心失活(无响应)')
                except Exception as e:
                    print('注册中心失活', str(e))
                finally:
                    self.regist_myself()

    def receive_heart(self, service_name):
        '''
        接收注册中心心跳接口
        :return: 心跳接收信息
        '''
        # print('收到心跳!!!')
        if reqq.is_json:
            reg_info = reqq.json
        else:
            reg_info = reqq.form.to_dict()
        self.update_reg_info(reg_info)

        # 检查自身注册信息是否正确
        if self.__prop['service_name'] == service_name:
            return jsonify({'event': 200, 'msg': '收到心跳'})
        else:
            # 自身实例注册信息有误
            return jsonify({'event': 404, 'msg': '收到心跳'})

    '''
    微服务调用单元列表初始化(暂时弃用 )
    '''

    # def micro_request_init(self,service,interface=[]):
    #     m_c_l=micro_cell_list()
    #     # 查找服务是否存在
    #     for ser in service:
    #         for inter in interface:
    #             if ser not in self.__reg_info.keys():
    #                 # 不存在已注册服务中提示警告
    #                 print('<警告>服务',ser,'未找到注册实例,接口',inter,'有失效风险')
    #                 m_c_l.append(micro_cell(ser,inter))
    #             else:
    #                 for ser_int in self.__reg_list_info[self.__reg_list_info[ser]]:
    #                     print(ser_int)

    def show_own_info(self):
        """
        展示自身信息
        :return:
        """
        return jsonify(self.__reg_info)


class e_dophon():
    '''

    服务器封装类(支持dophon实例)


    请求的发送和封装使用urllib3处理
    简单的一个基于flask服务器的一个实例

    '''

    __reg_url = 'http://localhost:8361/reg/service/'
    __reg_update_url = None
    __reg_info = {}
    __reg_heart = False

    '''
    增强app内部定义连接池(默认10个连接数)
    '''
    req_pool = urllib3.PoolManager()

    def __init__(self, service_name: str, reg_center_addr: tuple, instance=None):
        self.__dophon_instance = instance if instance else __import__('dophon.boot', fromlist=True)
        self.__dophon_app = getattr(self.__dophon_instance, 'app')
        # 读取服务器配置
        prop = __import__('dophon.cloud.client.properties', fromlist=True)
        # 写入服务名
        setattr(prop, 'service_name', service_name)
        # 写入注册中心信息
        setattr(prop, 'reg_url', '%s:%s%s' % reg_center_addr)
        # 启动微服务注册参数预处理流程
        if hasattr(prop, 'service_name'):
            self.__prop = {
                'service_name': prop.service_name.upper(),
                'health_interface': prop[
                    'health_interface'] if hasattr(prop, 'health_interface') else '/heart',
                'host': prop.host if hasattr(prop, 'host') else self.__host,
                'port': prop.port if hasattr(prop, 'port') and isinstance(prop.port,
                                                                          type(1)) else self.__port,
                'prefer_own_ip': prop.prefer_ip_str
                if hasattr(prop, 'prefer_ip_str') else
                socket.gethostbyname(socket.getfqdn(socket.gethostname()))
                if hasattr(prop, 'prefer_own_ip') and isinstance(prop.prefer_own_ip, type(True)) else
                False
            }
        else:
            raise Exception('缺少必要参数(service_name)')

        print('实例注册参数::', self.__prop)
        self.__reg_url = (prop.reg_url if hasattr(prop, 'reg_url') else self.__reg_url) + self.__prop[
            'service_name']
        self.__reg_update_url = re.sub('/reg/service/.*', '/reg/update', self.__reg_url)
        self.regist_myself()
        # 绑定自身功能接口
        self.__dophon_app.add_url_rule('/heart/as/<service_name>', 'receive_heart', self.receive_heart,
                                       methods=['POST'])
        self.__dophon_app.add_url_rule('/heart', 'show_own_info', self.show_own_info, methods=['POST'])

    def regist_myself(self):
        """
        向注册中心注册自身服务
        :return:
        """
        while True:
            try:
                # 向注册中心发起注册
                res = self.req_pool.request(method='get', url=self.__reg_url, headers={
                    'prefer_ip': self.__prop['prefer_own_ip']
                    if self.__prop['prefer_own_ip'] else self.__prop['host'],
                    'service_port': self.__prop['port']
                })
                self.__reg_list_info = eval(res.data.decode('utf8'))
                break
            except Exception as e:
                print('微服务(%s)启动失败!!,错误原因:: %s' % (self.__prop['service_name'].upper(), str(e)))
                print('30秒后重新注册')
                time.sleep(30)

    def service_name(self):
        return self.__prop['service_name']

    def port(self):
        return self.__prop['port']

    '''
    运行增强服务器
    '''

    def run(self, host=None, port=None, debug=None, **options):
        # 启动注册中心健康监测
        threading.Thread(target=self.check_reg_center).start()
        # 初始化注册服务实例(根据注册时返回的实例信息)
        self.__dophon_instance.run_app()

    '''
    更新微服务集群信息
    '''

    def update_reg_info(self, r):
        print('更新实例注册信息,', str(r), type(r))
        if not isinstance(r, type({})):
            for k in r.keys():
                v = r[k]
                r[k] = eval(v)
        self.__reg_info = r
        # 写入接收心跳标识
        if not self.__reg_heart:
            self.__reg_heart = True

    '''
    获取注册中心服务注册信息
    '''

    def reg_info(self):
        return self.__reg_info if self.__reg_info else self.__reg_list_info

    '''
    同步服务信息
    '''

    def async_reg_info(self):
        # 暂时使用重注册更新服务信息
        res = self.req_pool.request(method='get', url=self.__reg_update_url)
        result = eval(res.data.decode('utf8'))
        self.__reg_info = result
        return result

    def check_reg_center(self):
        if self.__reg_heart:
            # 存在接收心跳标识
            return
        else:
            # 定期检查注册中心
            while True:
                # 五分钟检查一次(默认)
                time.sleep(300)
                try:
                    res = self.req_pool.request(url=re.sub('/reg/service/.*', '/health', self.__reg_url), method='GET')
                    self.regist_myself()
                    print('注册中心存活' if res.status == 200 else '注册中心失活')
                except Exception as e:
                    print('注册中心失活', str(e))

    def receive_heart(self, service_name):
        '''
        接收注册中心心跳接口
        :return: 心跳接收信息
        '''
        # print('收到心跳!!!')
        if reqq.is_json:
            reg_info = reqq.json
        else:
            reg_info = reqq.form.to_dict()
        self.update_reg_info(reg_info)

        # 检查自身注册信息是否正确
        if self.__prop['service_name'] == service_name:
            return jsonify({'event': 200, 'msg': '收到心跳'})
        else:
            # 自身实例注册信息有误
            return jsonify({'event': 404, 'msg': '收到心跳'})

    '''
    微服务调用单元列表初始化(暂时弃用 )
    '''

    # def micro_request_init(self,service,interface=[]):
    #     m_c_l=micro_cell_list()
    #     # 查找服务是否存在
    #     for ser in service:
    #         for inter in interface:
    #             if ser not in self.__reg_info.keys():
    #                 # 不存在已注册服务中提示警告
    #                 print('<警告>服务',ser,'未找到注册实例,接口',inter,'有失效风险')
    #                 m_c_l.append(micro_cell(ser,inter))
    #             else:
    #                 for ser_int in self.__reg_list_info[self.__reg_list_info[ser]]:
    #                     print(ser_int)

    def show_own_info(self):
        """
        展示自身信息
        :return:
        """
        return jsonify(self.__reg_info)
