import argparse
import logging
import os
import signal
import threading

import pymq
from pymq.provider.redis import RedisConfig

from symmetry.common import config
from symmetry.common.cluster import ConfigNodeLister, RedisNodeManager
from symmetry.telemetry.telemd import TelemetryDaemon

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--power-disable', help='disable power logging', action='store_true', default=True)
    parser.add_argument('--power-interval', help='interval at which to probe power meter', type=float,
                        default=os.getenv('symmetry_power_sampling', 1))
    parser.add_argument('--agent-interval', help='interval at which to probe node agents', type=float,
                        default=os.getenv('symmetry_telemd_agent_interval', 1))
    parser.add_argument('--logging', required=False,
                        help='set log level (DEBUG|INFO|WARN|...) to activate logging',
                        default=os.getenv('symmetry_logging_level'))

    return parser.parse_args()


def main():
    args = parse_args()

    if args.logging:
        logging.basicConfig(level=logging._nameToLevel[args.logging])
        logging.getLogger('paramiko.transport').setLevel(logging.INFO)

    stopped = threading.Event()

    def handler(signum, frame):
        logger.info('signal received %s, triggering stopped', signum)
        stopped.set()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    rds = config.get_redis()
    pymq.init(RedisConfig(rds))

    # initialize nodes from node config
    nodes = ConfigNodeLister(config.get_nodes_config())
    node_manager = RedisNodeManager(rds)
    for node in nodes.nodes:
        node_manager.save_node(node)
    node_manager.synchronize_node_states()

    logger.info('starting telemetry daemon')
    td = TelemetryDaemon(node_manager, rds, args=args.__dict__)
    td.start()

    try:
        logger.debug('waiting for stopped signal ...')
        stopped.wait()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('stopping telemd...')
        try:
            td.stop()
        except KeyboardInterrupt:
            pass
        logger.info('telemd exiting')


if __name__ == '__main__':
    main()
