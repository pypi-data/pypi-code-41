# -*- coding: utf-8 -*-
"""Main module."""
import logging
import json
import time
import paho.mqtt.client as mqtt
from .topic import *

logger = logging.getLogger(__name__)


class AdapterMQTTNode:
    '''
    hbmqtt_pub --url mqtt://guest:test@iot.codelab.club -t 'eim/mqtt_gateway' -m "hello from hbmqtt"
    '''

    def __init__(self,
                 name='',
                 logger=logger,
                 mqtt_addr="iot.codelab.club",
                 mqtt_port=1883,
                 username="guest",
                 password="test",
                 mqtt_sub_topics=[TO_MQTT_TOPIC],
                 mqtt_pub_topic=TO_MQTT_TOPIC,
                 external_message_processor=None):
        # self.pub_topic = FROM_MQTT_TOPIC
        self._running = True
        self.name = name
        self.logger = logger
        self.mqtt_sub_topics = mqtt_sub_topics
        self.mqtt_pub_topic = TO_MQTT_TOPIC
        # mqtt settings
        self.mqtt_addr = mqtt_addr
        self.mqtt_port = 1883
        self.username = username
        self.password = password
        self.external_message_processor = external_message_processor

        # mqtt client
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.mqtt_addr, self.mqtt_port, 60)
        self.logger.info(f'''
        mqtt broker: {self.mqtt_addr}
        mqtt port: {self.mqtt_port}
        mqtt username: {self.username}
        mqtt password: {self.password}
        mqtt sub topics: {self.mqtt_sub_topics}
        mqtt pub topics: {self.mqtt_pub_topic}
        ''')

    def __str__(self):
        return self.name

    def mqtt_on_connect(self, client, userdata, flags, rc):
        self.logger.info(
            f"MQTT Gateway Connected to MQTT {self.mqtt_addr}:{self.mqtt_port} with result code {str(rc)}."
        )
        # when mqtt is connected to subscribe to mqtt topics
        if self.mqtt_sub_topics:
            if type(self.mqtt_sub_topics) is str:
                self.client.subscribe(self.mqtt_sub_topics)
            else:
                for sub in self.mqtt_sub_topics:
                    self.client.subscribe(sub)

    def mqtt_on_message(self, client, userdata, msg):
        '''
        use by monitor
        '''
        topic = msg.topic
        # self.logger.debug(f"topic type: {type(topic)}") # str
        if topic in self.mqtt_sub_topics:
            m = msg.payload.decode()  # 在通道的两端做好decode和encode
            payload = json.loads(m)  # json
            self.logger.debug(f'topic:{msg.topic} , payload: {payload}')
            if self.external_message_processor:
                self.external_message_processor(topic, payload)

    def send_message(self, payload):
        payload = json.dumps(payload).encode()
        self.client.publish(self.mqtt_pub_topic, payload)  # topic encode?

    def mqtt_payload_template(self):
        zmq_topic = ADAPTER_TOPIC
        zmq_payload = {"content": "", "extension_id": "", "sender": ""}
        payload = {"zmq_topic": zmq_topic, "zmq_payload": zmq_payload}
        return payload

    def run(self):
        self.client.loop_start()  # as thread
        while self._running:
            time.sleep(0.5)

    def clean_up(self):
        self._running = False
        self.client.loop_stop()

    def message_template(self):
        message_template = {
            "zmq_topic": ADAPTER_TOPIC,
            "zmq_payload": {
                "content": "content",
                "extension_id": self.EXTENSION_ID
            }
        }
        return message_template

    def publish(self, payload):
        payload["zmq_topic"] = ADAPTER_TOPIC  # 否则会死循环
        self.client.publish(FROM_MQTT_TOPIC, json.dumps(payload).encode())
