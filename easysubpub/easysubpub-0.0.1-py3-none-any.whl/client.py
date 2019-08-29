import json
from abc import ABCMeta, abstractmethod
from inspect import iscoroutinefunction
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class SubPubConfigBasic(metaclass=ABCMeta):
    def get_broker_host(self):
        return '127.0.0.1'

    def get_broker_port(self):
        return '5672'

    def get_broker_username(self):
        return 'rabbitmq'

    def get_broker_password(self):
        return '123456'

    def get_rabbitmq_subscribe_list(self):
        """
        :return:返回订阅的数组
        [
            'kkk', # 消息索引
            'yyy', # 消息索引
            ...
        ]
        """
        return []

    @abstractmethod
    def message_process_func(self):
        """
        1. subscribe_list is not empty
        2. when receive message, call this function to process message
        message 数据格式:
        {
            'organization':'hhh' # 组织信息
            'key'  : 'kkk',      # 消息索引
            'data' : 'lll'       # 消息数据
        }
        # 消息处理函数:
        def message_process_func(message):
            if msg['key'] == 'kkk':
                process kkk
            elif msg['key'] == 'yyy':
                process yyy

        :return:返回处理函数名(message_func_example)
        """
        pass

    def reconnect_interval(self):
        """
        :return:重连broker时间间隔, 默认 5 秒

        """
        return 5


class SubPubClient:
    def __init__(self, host='127.0.0.1', port=5672, username='rabbitmq', password='123456', queue_name=None,
                 subscribe_list=None, topic_list=None, message_process_func=None):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic_list = topic_list
        self.queue_name = queue_name
        self.subscribe_list = subscribe_list
        self.connection = None
        self.channel = None
        self.queue = None
        self.topic = {}
        self.subscribe_message_cache = {}
        self.publish_message_cache = {}
        self.message_process_func = message_process_func

    async def get_connection(self):
        # get rabbitmq connection ,if not exist create one
        from aio_pika import connect as aio_pika_connect
        # from aio_pika import  connect_robust as aio_pika_connect
        if not self.connection:
            try:
                self.connection = await aio_pika_connect(host=self.host, port=self.port, login=self.username,
                                                         password=self.password, socket_timeout=3,
                                                         heartbeat_interval=20)
                self.connection.add_close_callback(self.on_connection_closed)
                logging.info('connect rabbitmq success')
            except Exception as e:
                logging.error('connect rabbitmq failed, [host=%s],[port=%s],[username=%s],[password=%s]',
                              self.host, self.port, self.username, self.password)
                logging.error(e)
        return self.connection

    async def create_channel(self):
        # create rabbitmq channel ,if not exist create one
        if self.connection:
            self.channel = await self.connection.channel()
            logging.info('create rabbitmq channel success')
        return self.channel

    async def create_topic(self, topic_name):
        # create topic_type exchange with given topic_name
        from aio_pika import ExchangeType
        if self.channel and topic_name:
            exchange = await self.channel.declare_exchange(topic_name, ExchangeType.TOPIC)
            self.topic.update({topic_name: exchange})
            logging.info('create topic[%s] success', topic_name)
            if topic_name not in self.topic_list:
                self.topic_list.append(topic_name)
            return exchange

    async def create_topic_list(self, topic_list):
        # create topic_type exchange with given topic_list
        for topic_name in topic_list:
            await self.create_topic(topic_name)

    async def get_topic(self, topic_name):
        # get the topic_type exchange with given topic_name, if not exist create one
        exchange = self.topic.get(topic_name)
        if exchange is None:
            exchange = await self.create_topic(topic_name)

        logging.debug('get topic[%s] success', topic_name)
        return exchange

    async def create_queue(self, queue_name):
        # create a queue if not exist
        # 目前一个app对应一个queue
        if self.channel and queue_name:
            self.queue = await self.channel.declare_queue(queue_name, durable=True)
            logging.info('create queue:[%s] success', queue_name)

    async def init_topic_and_queue(self):
        # create channel\topic\queue,and bind topic exchange with subscribe_list
        logging.info('start rabbitmq init process')
        await self.create_channel()
        await self.create_topic_list(self.topic_list)
        await self.create_queue(self.queue_name)
        await self.bind_routing_key(self.subscribe_list, self.topic_list)

    async def publish_message(self, publish_key=None, publish_data=None, topic_name=None):
        # publish publish_key messages with topic exchange to queues,store the message if publish failed
        from aio_pika import Message, DeliveryMode

        if self.connection:
            exchange = await self.get_topic(topic_name)
            message_body = json.dumps(publish_data).encode('utf-8')
            message_data = Message(message_body, delivery_mode=DeliveryMode.PERSISTENT)
            await exchange.publish(message_data, routing_key=publish_key)
            logging.info('publish key[%s] message to topic[%s] success', publish_key, topic_name)
        else:
            logging.info('publish key[%s] message to topic[%s] failed because connection is None', publish_key,
                         topic_name)

    async def bind_routing_key(self, subscribe_key_list, topic_list):
        # bind queue and exchange with route_key
        if not topic_list:
            logging.warning('bind routing key failed because of topic_list is None')
            return

        if not self.queue:
            logging.warning('bind routing key failed because of queue is exist')
            return

        for topic_name in topic_list:
            exchange = await self.get_topic(topic_name)
            for subscribe_key in subscribe_key_list:
                await self.queue.bind(exchange, routing_key=subscribe_key)
                logging.info('bind subscribe key[%s] to topic[%s] success', subscribe_key, topic_name)
                if subscribe_key not in self.subscribe_list:
                    self.subscribe_list.append(subscribe_key)

    async def unbind_routing_key(self, routing_key_list, topic_list):
        for topic_name in topic_list:
            for routing_key in routing_key_list:
                await self.queue.unbind(topic_name, routing_key)
                logging.info('unbind routing_key[%s] to topic[%s]', routing_key, topic_name)
                if routing_key in self.subscribe_list:
                    self.subscribe_list.remove(routing_key)

    async def listening_message(self):
        # 监听队列消息
        from aio_pika import IncomingMessage
        async def receive_message_callback(message: IncomingMessage):
            # 调用回调函数处理消息
            with message.process(ignore_processed=True):
                message.ack()
                topic_name = message.exchange
                routing_key = message.routing_key

                if routing_key not in self.subscribe_list:
                    await self.unbind_routing_key([routing_key], [topic_name])
                    logging.info('subscribe_key[%s] not exist in subscribe_list', routing_key)
                    return

                message_body = json.loads(message.body.decode("utf-8"))
                logging.debug('receive rabbitmq message from topic[%s] by routing_key[%s]', topic_name,
                              routing_key)
                logging.debug('message_body==%s', message_body)

                exectue_message = {'topic': topic_name, 'key': routing_key, 'data': message_body}
                await self.exectue_message_process_func(exectue_message)

        if self.queue:
            await self.queue.consume(receive_message_callback)

    async def exectue_message_process_func(self, exectue_message):
        # 执行用户注册的消息处理函数
        if self.message_process_func:
            if iscoroutinefunction(self.message_process_func):
                await self.message_process_func(exectue_message)
            else:
                self.message_process_func(exectue_message)

    def on_connection_closed(self, future):
        logging.warning('on_connection_closed')


async def rabbitmq_async_connect(host='127.0.0.1', port=5672, username=None, password=None, queue_name=None,
                                 subscribe_list=None, topic_list=None, message_process_func=None):
    broker_handler = SubPubClient(host, port, username, password, queue_name, subscribe_list, topic_list,
                                  message_process_func)

    await broker_handler.get_connection()  # create connection
    if broker_handler.connection:
        await broker_handler.init_topic_and_queue()

    logging.info('rabbitmq_async_connect success')
    return broker_handler
