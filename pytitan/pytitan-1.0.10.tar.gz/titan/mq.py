# coding: utf-8
import pika
import json
import logging
import threading
from datetime import datetime, date
from bson import ObjectId
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)


class ExchangeTypes():
    DEFAULT = 'default'
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = 'topic'


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
            return dict(obj)
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, date):
            # return obj.strftime('%Y-%m-%d')
            return obj.strftime('%Y-%m-%dT%H:%M:%S')  # mongodb的date类型为python的datetime类型
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class AMQPClient():
    """
    定义可连接至RabbitMQ的基类
    """
    _connection = None
    host = 'localhost'
    channel = None
    exchange = None
    queue = None
    exchange_type = ExchangeTypes.DEFAULT
    user = None
    pwd = None

    def create_connection_parameters(self):
        # 身份验证凭证
        if self.user is not None and self.pwd is not None:
            return pika.ConnectionParameters(credentials=pika.PlainCredentials(self.user, self.pwd),
                                             host=self.host)
        else:
            return pika.ConnectionParameters(host=self.host)

    def create_connection(self):
        """
        创建Rabbit连接的工厂方法，默认使用 SelectionConnection自动选择连接
        :param kwargs:
        :return:
        """
        return pika.BlockingConnection(self.create_connection_parameters())

    def connect(self):
        self._connection = self.create_connection()
        self.on_connection_open()
        self.channel = self._connection.channel()
        self.setup_exchange()

    def reconnect(self):
        if self._connection is None or self._connection.is_closed:
            self.connect()

    def close(self):
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
            self.on_connection_close()

    def on_connection_open(self):
        pass

    def on_connection_close(self):
        pass

    def setup_exchange(self):
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type=self.exchange_type)

    def setup_queue(self, **kwargs):
        result = self.channel.queue_declare(**kwargs)
        # result = self.channel.queue_declare(exclusive=True)
        self.queue = result.method.queue


class TopicAMQPClient(AMQPClient):
    exchange_type = ExchangeTypes.TOPIC

    def __init__(self, exchange):
        """
        :param exchange: 主题交换机名称
        :param topic: 主题名
        """
        if exchange is None or exchange == '':
            raise ValueError("主题交换机名称不能为空")

        self.exchange = exchange


class TopicProducer(TopicAMQPClient):
    """
    主题消息生产者（发送方)
    """

    def emit(self, topic, message):
        """
        向主题交换机发送消息
        :param message:
        :return:
        """
        if message == '' or message is None:
            raise ValueError("不能发送空内容")

        self.reconnect()

        if self.channel is None:
            raise RuntimeError("消息队列通道尚未初始化")

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=topic,
                                   body=message)
        self.close()

    def emit_json(self, topic, message):
        self.emit(topic, json.dumps(message, cls=CJsonEncoder))


class TopicConsumer(TopicAMQPClient):
    """
    主题消息消费方（接收方）
    """
    _callbacks = []
    _background = None

    def __call__(self, topic, auto_ack=True):

        def _(func):
            self._callbacks.append((topic, auto_ack, func))

        return _

    def __del__(self):
        self.stop()

    def start(self):
        self.connect()

        self.setup_queue(queue='', exclusive=True)

        topics = set([t for t, _, f in self._callbacks])

        for topic in topics:
            self.channel.queue_bind(exchange=self.exchange,
                                    queue=self.queue,
                                    routing_key=topic)

        for _, ack, _cb in self._callbacks:
            self.channel.basic_consume(on_message_callback=_cb,
                                       queue=self.queue,
                                       auto_ack=ack)

        self._background = threading.Thread(target=self._start_consuming)
        self._background.start()

    def _start_consuming(self):
        self.channel.start_consuming()

    def stop(self):
        if self._background is not None:
            self.close()
            self._background.join()


class RabbitMQ():
    consumers = []

    def __init__(self, app=None, consumer=None):
        self.host = None
        self.username = None
        self.password = None

        if app is not None:
            self.init(app)
            self.valid_config()

        if consumer is not None:
            self.register_consumer(consumer)

    def init(self, app):
        if app is None:
            raise RuntimeError("App 不能为空")
        self.app = app
        self.config = app.config

    def valid_config(self):
        if not self.config.get('RABBITMQ_HOST'):
            raise Exception("The rabbitMQ application must configure host.")
        self.host = self.config.get('RABBITMQ_HOST')
        self.username = self.config.get('RABBITMQ_USERNAME')
        self.password = self.config.get('RABBITMQ_PASSWORD')

    def _init_client(self, client):
        client.user = self.username
        client.pwd = self.password
        client.host = self.host

    def register_consumer(self, consumer):
        self._init_client(consumer)
        self.consumers.append(consumer)

    def send(self, exchange, topic, message):
        producer = TopicProducer(exchange=exchange)
        self._init_client(producer)
        producer.emit(topic, message)

    def run(self):
        [consumer.start() for consumer in self.consumers]
