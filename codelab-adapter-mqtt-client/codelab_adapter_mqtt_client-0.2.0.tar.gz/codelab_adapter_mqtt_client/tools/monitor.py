import argparse
import signal
import sys

from codelab_adapter_mqtt_client import AdapterMQTTNode
from codelab_adapter_mqtt_client.topic import *

from loguru import logger

class Monitor(AdapterMQTTNode):
    """
    This class subscribes to all adapter mqtt messages and prints out both topic and payload.
    """
    def __init__(self, *args, **kwargs):
        kwargs["logger"] = logger
        kwargs["mqtt_sub_topics"] = [FROM_MQTT_TOPIC, TO_MQTT_TOPIC]
        super().__init__(*args, **kwargs)

def monitor():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", dest="mqtt_addr", default="iot.codelab.club",
                        help="mqtt broker address")
    parser.add_argument("-n", dest="name", default="Monitor", help="set name in banner")
    parser.add_argument("-p", dest="mqtt_port", default='1883',
                        help="mqtt broker port")
    parser.add_argument("-u", dest="username", default='guest',
                        help="mqtt username")
    parser.add_argument("-k", dest="password", default='test',
                        help="mqtt password")
    parser.add_argument("-m", dest="mqtt_sub_topics", default=None,
                        help="mqtt sub topic")     

    args = parser.parse_args()
    kw_options = {}

    kw_options['mqtt_addr'] = args.mqtt_addr
    kw_options['name'] = args.name
    kw_options['mqtt_port'] = args.mqtt_port
    kw_options['username'] = args.username
    kw_options['password'] = args.password
    if args.mqtt_sub_topics:
        kw_options['mqtt_sub_topics'] = args.mqtt_sub_topics

    my_monitor = Monitor(**kw_options)
    my_monitor.client.on_message = my_monitor.mqtt_on_message
    

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')
        my_monitor.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    my_monitor.run()

if __name__ == '__main__':
    monitor()
