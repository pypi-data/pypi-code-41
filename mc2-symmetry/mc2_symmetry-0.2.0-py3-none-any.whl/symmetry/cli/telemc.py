import argparse
import logging
import signal

import redis

from symmetry.telemetry.recorder import TelemetryFileRecorder, TelemetryPrinter, TelemetryRedisRecorder


def handler(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    # TODO: mutually exclusive group
    parser.add_argument('--print', help='print to system out', action='store_true')
    parser.add_argument('--file', '-f', metavar='path', help='write to a file')
    parser.add_argument('--redis', help='write to redis', action='store_true')
    args = parser.parse_args()

    rds = redis.Redis(decode_responses=True)

    if args.file:
        td = TelemetryFileRecorder(rds, args.file)
    elif args.redis:
        td = TelemetryRedisRecorder(rds)
    else:
        td = TelemetryPrinter(rds)

    try:
        td.run()
    except KeyboardInterrupt:
        pass
    finally:
        td.close()


if __name__ == '__main__':
    main()
