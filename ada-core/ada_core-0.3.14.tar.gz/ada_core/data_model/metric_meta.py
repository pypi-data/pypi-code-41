"""
Author: qiacai
"""
import pytz

from schematics.models import Model
from schematics.types import StringType


class MetricMeta(Model):

    name = StringType(required=True)
    timezone = StringType(choices=pytz.all_timezones)

    def __init__(self, name: str, timezone: str):

        super(Model, self).__init__()
        self.name = name
        self.timezone = timezone
        self.validate()