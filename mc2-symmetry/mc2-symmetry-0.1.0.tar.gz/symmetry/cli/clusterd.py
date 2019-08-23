import argparse
import logging
import os
import signal
import threading

import pymq
import redis
from pymq.provider.redis import RedisConfig

from symmetry.clusterd import RedisClusterInfo, BalancingPolicyDaemon
from symmetry.routing import RedisRoutingTable

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--redis-host', help='hostname of the Redis instances', type=str,
                        default=os.getenv('REDIS_HOST', 'localhost'))
    parser.add_argument('--logging', required=False,
                        help='set log level (DEBUG|INFO|WARN|...) to activate logging')

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

    logger.debug("connecting to redis host %s", args.redis_host)
    rds = redis.Redis(host=args.redis_host, decode_responses=True)

    pymq.init(RedisConfig(rds))

    logger.info('starting balancing policy runner')
    bpd = BalancingPolicyDaemon(RedisClusterInfo(rds), RedisRoutingTable(rds))
    bpd_thread = threading.Thread(target=bpd.run, name='balancing-policy-runner')
    bpd_thread.start()

    try:
        logger.debug('waiting for stopped signal ...')
        stopped.wait()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('stopping clusterd...')
        try:
            bpd.close()
            bpd_thread.join()
        except KeyboardInterrupt:
            pass

    logger.info('clusterd exiting')


if __name__ == '__main__':
    main()
