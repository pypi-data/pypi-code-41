from datetime import datetime

import pytz


def build_alg_now():
    return pytz.UTC.localize(datetime.utcnow())
