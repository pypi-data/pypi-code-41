import argparse
import logging
import os
import signal
import threading

from symmetry.common import config
from symmetry.telemetry.power import PowerMonitor

logger = logging.getLogger(__name__)


def main():
    log_level = os.getenv('symmetry_logging_level')
    if log_level:
        logging.basicConfig(level=logging._nameToLevel[log_level])

    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', help='sampling interval', type=float,
                        default=os.getenv('symmetry_power_sampling'))

    args = parser.parse_args()

    monitor = threading.Condition()

    def handler(signum, frame):
        logger.info('signal received %s', signum)
        with monitor:
            monitor.notify()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    rds = config.get_redis()
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
