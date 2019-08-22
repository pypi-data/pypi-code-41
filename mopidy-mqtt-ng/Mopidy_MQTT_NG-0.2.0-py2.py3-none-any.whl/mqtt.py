import logging
from os import getpid

from paho.mqtt import client as mqtt


log = logging.getLogger(__name__)


HANDLER_PREFIX = 'on_action_'


class Comms(object):
    def __init__(self, frontend, config):
        """
        Configure MQTT communication client.

        frontend (MQTTFrontend): Instance of extension's frontend.
        config (dict): Current extension configuration.
        """
        self.frontend = frontend
        self.config = config

        self.client = mqtt.Client(
            client_id='mopidy-{}'.format(getpid()), clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start(self):
        """
        Attempt connection to MQTT broker and initialise network loop.
        """
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 1883)
        user = self.config.get('user', None)
        password = self.config.get('password', None)

        if user and password:
            self.client.username_pw_set(username=user, password=password)

        self.client.connect_async(host=host, port=port)
        log.debug('Connecting to MQTT broker at %s:%s', host, port)
        self.client.loop_start()
        log.debug('Started MQTT communication loop.')

    def stop(self):
        """
        Clean up and disconnect from MQTT broker.
        """
        self.client.disconnect()
        log.debug('Disconnected from MQTT broker')

    def _on_connect(self, client, userdata, flags, rc):
        log.info('Successfully connected to MQTT broker, result :%s', rc)
        # Namespace for controlling Mopidy behaviour.
        prefix = self.config.get('topic', 'mopidy')

        for name in dir(self.frontend):
            if not name.startswith(HANDLER_PREFIX):
                continue

            suffix = name[len(HANDLER_PREFIX):]
            topic = '{}/{}'.format(prefix, suffix)
            result, _ = self.client.subscribe(topic)

            if result == mqtt.MQTT_ERR_SUCCESS:
                log.debug('Subscribed to MQTT topic: %s', topic)
            else:
                log.warn('Failed to subscribe to MQTT topic: %s, result: %s',
                         topic, result)

    def _on_message(self, client, userdata, message):
        topic = message.topic.split('/')[-1]

        handler = getattr(self.frontend, HANDLER_PREFIX + topic, None)
        if not handler:
            log.warn('Cannot handle MQTT messages on topic: %s', message.topic)
            return

        log.debug('Passing payload: %s to MQTT handler: %s',
                  message.payload, handler.__name__)
        handler(value=message.payload)

    def publish(self, subtopic, value):
        prefix = self.config.get('topic', 'mopidy')
        topic = '{}/{}'.format(prefix, subtopic)

        log.debug('Publishing: %s to MQTT topic: %s', value, topic)
        return self.client.publish(topic=topic, payload=value)
