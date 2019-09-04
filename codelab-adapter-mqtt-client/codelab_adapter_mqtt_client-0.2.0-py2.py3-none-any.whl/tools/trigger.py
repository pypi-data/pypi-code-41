import argparse
import signal
import sys
import json
import time

from codelab_adapter_mqtt_client import AdapterMQTTNode

from codelab_adapter_mqtt_client.topic import *
from codelab_adapter_mqtt_client.utils import threaded

from loguru import logger

class Trigger(AdapterMQTTNode):
    """
    This class subscribes to all adapter mqtt messages and prints out both topic and payload.
    """

    def __init__(self, *args, **kwargs):
        kwargs["logger"] = logger
        super().__init__(*args, **kwargs)
        self._running = True

    def run(self):
        while self._running:
            # print(">>>self.publish({'topic':EXTENSIONS_OPERATE_TOPIC,'payload':{'content':'start', 'extension_id':'extension_eim2'}})")
            code = input(">>>read json from /tmp/mqtt_message.json (enter to run)")
            with open("/tmp/mqtt_message.json") as f:
                json_string = f.read()
                # message = json.loads()
            self.client.publish(FROM_MQTT_TOPIC, json_string.encode())
            print("ok!")


def trigger():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        dest="mqtt_addr",
        default="iot.codelab.club",
        help="mqtt broker address")
    parser.add_argument(
        "-n", dest="name", default="Monitor", help="set name in banner")
    parser.add_argument(
        "-p", dest="mqtt_port", default='1883', help="mqtt broker port")
    parser.add_argument(
        "-u", dest="username", default='guest', help="mqtt username")
    parser.add_argument(
        "-k", dest="password", default='test', help="mqtt password")

    args = parser.parse_args()
    kw_options = {}

    kw_options['mqtt_addr'] = args.mqtt_addr
    kw_options['name'] = args.name
    kw_options['mqtt_port'] = args.mqtt_port
    kw_options['username'] = args.username
    kw_options['password'] = args.password

    my_trigger = Trigger(**kw_options)
    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')
        my_trigger.clean_up()
        time.sleep(0.1)
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    my_trigger.run()

if __name__ == '__main__':
    trigger()
