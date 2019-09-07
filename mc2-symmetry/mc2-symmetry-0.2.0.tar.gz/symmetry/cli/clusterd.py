import argparse
import logging
import os
import signal
import threading

import pymq
from pymq.provider.redis import RedisConfig

from symmetry.clusterd import RedisClusterInfo, BalancingPolicyDaemon, NodeManagerDaemon
from symmetry.common import config
from symmetry.common.cluster import RedisNodeManager
from symmetry.routing import RedisRoutingTable

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
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

    logger.info('starting balancing policy runner')
    bpd = BalancingPolicyDaemon(RedisClusterInfo(rds), RedisRoutingTable(rds))
    bpd_thread = threading.Thread(target=bpd.run, name='balancing-policy-runner')
    bpd_thread.start()

    noded = NodeManagerDaemon(RedisNodeManager(rds))  # doesn't need to start

    try:
        logger.debug('waiting for stopped signal ...')
        stopped.wait()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('stopping clusterd...')
        try:
            noded.close()
            bpd.close()
            logger.debug('waiting on BalancingPolicyDaemon to exit')
            bpd_thread.join()
        except KeyboardInterrupt:
            pass

    logger.info('clusterd exiting')


if __name__ == '__main__':
    main()
