import argparse
import logging
import os
import signal
import threading

import redis

from symmetry.telemetry.power import PowerMonitor

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', help='sampling interval', type=float)
    parser.add_argument('--redis-host', help='hostname of the Redis instances', type=str,
                        default=os.getenv('REDIS_HOST', 'localhost'))

    args = parser.parse_args()

    monitor = threading.Condition()

    def handler(signum, frame):
        logger.info('signal received %s', signum)
        with monitor:
            monitor.notify()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    logging.debug("connecting to redis host %s", args.redis_host)
    rds = redis.Redis(host=args.redis_host, decode_responses=True)

    logging.info('starting power monitor')
    powmon = PowerMonitor(rds, interval=args.interval)

    try:
        powmon.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('stopping power monitor...')
        powmon.cancel()


if __name__ == '__main__':
    main()
