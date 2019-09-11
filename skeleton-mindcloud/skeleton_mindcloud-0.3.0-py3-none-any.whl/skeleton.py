from pyhocon import ConfigFactory
from confluent_kafka import Consumer, KafkaError, Message, Producer

import os
import logging
import json
from datetime import datetime

__doc__="""Small library to develop MindCloud apps in python"""
__version__= "0.3.0"

def client_message(id, type, message, timestamp=datetime.now().isoformat()):
    return json.dumps(dict(id=id, messageType=type, message=message, timeStamp=timestamp))

class MessageHandler(object):

    def __delivery_report(self, err, msg):
        if err is not None:
            self.logger.error("Message delivery failed: {}".format(err))
        else:
            self.logger.info("Message '{}:{}'delivered to {} [{}]".format(msg.key(), msg.value(), msg.topic(), msg.partition()))

    def __create_kafka(self):
        if 'kafka.brokers' not in self.conf:
            raise KeyError('kafka brokers are not defined in application.conf')
        self.bootsrap_servers = self.conf.get('kafka.brokers')
        self.logger.info("kafka bootsrap.servers: {}".format(self.bootsrap_servers))

        if 'messaging.input' in self.conf:
            self.input_topic = self.conf.get('messaging.input')
            self.logger.info("input topic : {}".format(self.input_topic))
            if 'messaging.group' not in self.conf:
                raise KeyError('No group id defined in application.conf')
            else:
                self.group_id = self.conf.get('messaging.group')            
                self.logger.info("group id: {}".format(self.group_id))
                self.__create_consumer()
        if 'messaging.output' in self.conf:
            self.output_topic = self.conf.get('messaging.output')
            self.logger.info("Output topic: {}".format(self.output_topic))
            self.__create_producer()
        if 'messaging.client' in self.conf:
            self.client_topic = self.conf.get('messaging.client')
            self.logger.info("Client topic: {}".format(self.client_topic))
            self.has_client = True

    def log(self, correlationId, message):
        return '|'+correlationId.decode('utf-8')+'| '+ message

    def send_client_message(self, msg):
        if self.has_client:
            self.producer.poll(0)
            self.producer.produce(self.client_topic, msg, callback=self.__delivery_report)
            self.producer.flush()
        else:
            self.logger.error("Client topic was not defined")

    def __create_consumer(self):
        self.logger.info('Create consumer')
        self.consumer = Consumer(
            {'bootstrap.servers': self.bootsrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'latest'})
        self.has_consumer = True

    def __create_producer(self):
        self.logger.info('Create producer')
        self.producer = Producer({'bootstrap.servers': self.bootsrap_servers})
        self.has_producer = True

    def __init__(self, name):
        self.has_producer = False
        self.has_consumer = False
        self.has_client = False
        configurations = os.getenv('CONFIG_FILES', 'application.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(format='%(asctime)s - {} - %(levelname)s - %(message)s'.format(name), level=logging.INFO)
        self.conf = ConfigFactory.parse_file(configurations)
        self.__create_kafka()

class MessageSource(MessageHandler):

    def handle_input(self, handler, output=None):
        try:
            self.consumer.subscribe([self.input_topic])
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    self.logger.error('Message consumer failed: {}'.format(msg.error()))
                self.logger.info("received message: {} {}".format(msg.key(), msg.value()))
                result = handler(msg.key(), msg.value())
                if result is not None and output is not None:
                    output(result[0], result[1])
        except Exception as ex:
            self.logger.exception(ex)
            self.logger.error("Can't subscribe to topic {}".format(self.input_topic))

class MessageSink(MessageHandler):

    def delivery_report(self, err, msg):
        if err is not None:
            self.logger.error("Message delivery failed: {}".format(err))
        else:
            self.logger.info("Message '{}:{}'delivered to {} [{}]".format(msg.key(),msg.value(), msg.topic(), msg.partition()))


    def handle_output(self, key, value):
        self.producer.poll(0)
        self.producer.produce(topic=self.output_topic,key=key,value=value, callback=self.delivery_report)
        self.producer.flush()

class MessageFlow(MessageSink, MessageSource):
    def handle_input_output(self, handler_func):
        self.handle_input(handler_func, self.handle_output)

if __name__ == '__main__':
    class MySource(MessageSink):
        def myhandler(self, key, value):
            print("received: {} {}".format(key, value))
    m = MySource("SOURCEOM")
    m.handle_output("alma","korte")        


