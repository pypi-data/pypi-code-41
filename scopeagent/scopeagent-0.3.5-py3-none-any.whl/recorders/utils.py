import logging

from ..vendor import ntplib


logger = logging.getLogger(__name__)
offset = None


def fix_timestamps(span):
    global offset
    if offset is None:
        try:
            offset = ntplib.NTPClient().request("pool.ntp.org", version=3).offset
            logger.debug("detected time offset using NTP: %f", offset)
        except Exception as e:
            logger.debug("could not determine time offset using NTP: %s", e)
            offset = 0

    span.start_time += offset
    for event in span.logs:
        event.timestamp += offset

    return span
