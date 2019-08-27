import random
import time


def source_random(**kwargs):
    min = kwargs.get('min', 0.0)
    max = kwargs.get('max', 100.0)
    digits = kwargs.get('digits', 2)
    sleep = kwargs.get('sleep', 0)

    time.sleep(sleep)

    return round(random.uniform(min, max), digits)
