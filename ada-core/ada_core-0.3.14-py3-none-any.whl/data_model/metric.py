"""
Author: qiacai
"""

from schematics.models import Model
from schematics.types import ModelType

from ada_core.data_model.time_series import TimeSeries
from ada_core.data_model.metric_meta import MetricMeta
from ada_core.data_model.io_data_type import TimeSeriesType


class Metric(Model):
    time_series = TimeSeriesType(required=True)
    metric_meta = ModelType(MetricMeta)

    def __init__(self, time_series: TimeSeries, metric_meta: MetricMeta):

        super(Model, self).__init__()
        self.time_series = time_series
        self.metric_meta = metric_meta
        self.validate()