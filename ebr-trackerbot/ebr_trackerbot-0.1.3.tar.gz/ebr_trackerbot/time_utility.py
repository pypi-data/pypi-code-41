"""
Holds utility functions for the package
"""

import re
import pendulum


def parse_time_delta_input(time_delta_raw, start_time=pendulum.now("UTC")):
    """
    Handle parsing a time delta string provided by the user into an actual time
    Args:
        time_delta_raw: input string from the user, the time interval can contain *s* - seconds, *m* - minutes, *h* - hours, *d* - days
        start_time: Pendulum date-time object to apply the time delta to. Defaults to now, UTC

    """
    time_delta = start_time
    parts = re.split("([smhdy])", time_delta_raw)
    number = None
    for part in parts:
        if part in ["s", "m", "h", "d"] and number is not None:
            if part == "s":
                time_delta = time_delta.subtract(seconds=number)
            if part == "m":
                time_delta = time_delta.subtract(minutes=number)
            if part == "h":
                time_delta = time_delta.subtract(hours=number)
            if part == "d":
                time_delta = time_delta.subtract(days=number)
        else:
            try:
                number = int(part)
            except ValueError:
                number = None

    return time_delta
