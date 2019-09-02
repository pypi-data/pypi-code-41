import numpy as np
from more_itertools import windowed

from .curve_element import Jump, Point

__all__ = ['generate_curve']


RESOLUTION = 600
MAXIMUM_ERROR = 1e-8


def generate_curve(curve_source, *, fill):
    def slope(a, b):
        deltas = np.array(b) - np.array(a)
        if deltas[0] == 0:
            return np.inf
        return deltas[1] / deltas[0]

    def get_last_key_time(element):
        point_key = element.latest_key
        last_time = element.latest_time()
        return point_key, last_time

    def yield_points(first_point_key, first_point_time, last_point_time):
        delta_time = last_point_time - first_point_time
        if delta_time <= 0:
            return
        times = np.linspace(first_point_time,
                            last_point_time,
                            max(1, delta_time / max_absorb_period))
        times_and_values = [
            np.array((time, curve_source.get_value(first_point_key, time)))
            for time in times] + [None]
        for three_times_and_values in windowed(times_and_values, 3):
            if three_times_and_values[1] is None:
                break
            if (three_times_and_values[2] is not None
                    and np.isclose(
                        slope(three_times_and_values[0],
                              three_times_and_values[1]),
                        slope(three_times_and_values[0],
                              three_times_and_values[2]),
                        rtol=MAXIMUM_ERROR)):
                continue
            time, value = three_times_and_values[1]
            yield Point(latest_key=first_point_key,
                        time=time,
                        value=value)

    max_absorb_period = ((curve_source.end_time - curve_source.start_time)
                         / RESOLUTION)
    element = None

    # Generate a Point or Jump for the first key.
    key = curve_source.get_last_key()
    time = curve_source.start_time
    value = float(curve_source.get_value(key, time).real)
    if value == 0.0:
        element = Point(latest_key=key, time=time, value=value,
                        no_absorb=True)
    else:
        element = Jump(latest_key=key, time=time, value=value, jump_from=0.0,
                       no_absorb=True)

    for key, time in curve_source.keys_and_times():
#       if key == last_key_emitted:
#           assert time == last_time_emitted

        value = float(curve_source.get_value(key, time).real)

        # Absorb additional "elements" from curve_source into the last
        # element.
        if ((time < element.time + max_absorb_period)
                and not element.no_absorb):
            absorbed = element.absorb(key, time, value)
            if absorbed:
                element = absorbed
                continue

        # Now that we have an element that could not be absorbed, emit
        # the last element and all the points between it and now.
        last_key, last_time = get_last_key_time(element)
        yield element
        yield from yield_points(last_key, last_time, time)

        element = Jump(latest_key=key,
                       time=time,
                       value=value,
                       jump_from=curve_source.get_value(last_key, time),
                       no_absorb=False)

    last_key, last_time = get_last_key_time(element)
    yield element
    yield from yield_points(last_key, last_time, curve_source.end_time)

    if fill:
        yield Point(latest_key=last_key,
                    time=curve_source.end_time,
                    value=0.0)
