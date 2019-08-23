import logging
import os

import redis

from symmetry.telemetry.recorder import TelemetryDashboardRecorder


def on_starting(server):
    # simple way of getting the logs to output by reusing gunicorn's --log-level config
    logging.basicConfig(level=logging.getLogger('gunicorn.error').level)

    redis_host = os.getenv('REDIS_HOST', 'localhost')

    rds = redis.Redis(host=redis_host, decode_responses=True)

    server.telemc = TelemetryDashboardRecorder(rds)
    server.telemc.start()


def on_exit(server):
    server.telemc.stop()
