from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, StringField, UInt64Field
from .db import CLUSTER_NAME, Model, DistributedModel

class AutotestsResourcesMonitoring(Model):
    day = DateField()
    created_on = DateTimeField()
    state = StringField()
    platform = StringField()
    account = StringField()
    step = StringField()
    fps = UInt64Field()
    all_objects_size = fields.Float64Field()
    textures_size = fields.Float64Field()
    unity_allocated_memory = fields.Float64Field()
    total_memory_reserved = fields.Float64Field()
    fps_end = UInt64Field()
    all_objects_size_end = fields.Float64Field()
    textures_size_end = fields.Float64Field()
    unity_allocated_memory_end = fields.Float64Field()
    total_memory_reserved_end = fields.Float64Field()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('platform', 'created_on'))


class AutotestsResourcesMonitoringDist(AutotestsResourcesMonitoring, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)