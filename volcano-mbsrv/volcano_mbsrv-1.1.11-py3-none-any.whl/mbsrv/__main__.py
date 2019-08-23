#!/usr/bin/python3
import sys
import argparse
import logging

from twisted.internet import reactor
from twisted.internet.error import CannotListenError

# volcano
from volcano.general.log import configure_arg_parser_for_log, configure_logger
from volcano.general.stddef import VOLCANO_DEFAULT_TCP_PORT
from volcano.general.xml_reader import load_xml_file_le, XmlReader, LoadException
from volcano.general.stdsvc import SingleThreadAllService

from volcano.twistedclient.twisted_factory import VolcanoTwistedFactory
from volcano.twistedclient.twisted_client_st import VolcanoTwistedClientST

from . import device
from .mb_server import MbFactory


def configure_my_args(parser):
    parser.add_argument('--core_host', help='Volcano core host', default='localhost')
    parser.add_argument('--core_port', help='Volcano core port', default=VOLCANO_DEFAULT_TCP_PORT, type=int)
    parser.add_argument('-n', '--name', help='Instance name', default='mbsrv')
    parser.add_argument('-f', '--file', help='Config file', default='mbsrv.xml')
    parser.add_argument('-i', '--iface', help='Listen interface', default='')
    parser.add_argument('-p', '--port', help='ModbusTCP port', type=int)
    parser.add_argument('--max_con', help='Max number of connections', type=int, default=2)


def override_xml_env(name: str, xml_val, env_val, default_val, log):
    if not xml_val and not env_val:
        log.info('%s set to default value %s', name, default_val)
        return default_val
    elif xml_val and env_val:
        log.info('%s set to %s because command line has priority over xml (in xml value is %s)', name, env_val, xml_val)
        return env_val
    elif xml_val:
        assert not env_val, env_val
        return xml_val
    else:
        return env_val

# ! LoadException
def load(env, log) -> list:
    file = load_xml_file_le(env.file)

    p = XmlReader(file.getroot())
    devices = []

    env.iface = override_xml_env('Interface', p.get_str('iface', ''), env.iface, '0.0.0.0', log)
    env.port = override_xml_env('Port', p.get_int('port', 0, min_val=1, max_val=0xffff), env.port, 502, log)

    for node in file.getroot():
        if node.tag == 'Device':
            dev = device.Device(node, log)
            devices.append(dev)
        else:
            raise LoadException('Unknown node name: "{}"'.format(node.tag))

    if not devices:
        raise LoadException('No devices configured')

    return devices


class MyLavaClient(VolcanoTwistedClientST):
    def __init__(self, env, devices):
        super().__init__(logging.getLogger(env.name))
        self.env = env
        self.devices = devices
        self.all_svc_ = None

    def connectionMade(self):
        super().connectionMade()

        self.all_svc_ = SingleThreadAllService(self)
        self.all_svc_.salute(self.env.name)

        for dev in self.devices:
            dev.sync(self.all_svc_, self.all_svc_, self.all_svc_)
        self.all_svc_.echo(self.sync_complete)

    def sync_complete(self):
        self.log.info('Start listen: iface=%s port=%s', self.env.iface, self.env.port)
        try:
            reactor.listenTCP(self.env.port, MbFactory(self.devices, self.env), interface=self.env.iface)   # pylint: disable=no-member
        except CannotListenError as ex:
            self.log.error(ex)
            reactor.stop()      # pylint: disable=no-member

    def on_msg_rcvd_no_exc(self, msg: dict) -> None:   # Exceptions not expected
        self.all_svc_.push_single_message(msg)


def main():
    try:
        # Args
        arg_parser = argparse.ArgumentParser()
        configure_my_args(arg_parser)
        configure_arg_parser_for_log(arg_parser)  # let logger add his arguments for later configure_logger() call
        env = arg_parser.parse_args()

        # Logging
        configure_logger(env)
        log = logging.getLogger(env.name)

        try:
            devices = load(env, log)
        except LoadException as ex:
            log.error(ex)
            return 1

        volcano_factory = VolcanoTwistedFactory()
        volcano_factory.log = log
        volcano_factory.client = MyLavaClient(env, devices)

        log.info('Connect to core at %s:%s', env.core_host, env.core_port)
        reactor.connectTCP(env.core_host, env.core_port, volcano_factory)           # pylint: disable=no-member
        reactor.run()                                                               # pylint: disable=no-member

        return 0
    finally:
        logging.shutdown()


if __name__ == '__main__':
    sys.exit(main())
