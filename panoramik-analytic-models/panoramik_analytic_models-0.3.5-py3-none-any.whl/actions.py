from infi.clickhouse_orm import engines

from .fields import DateField, DateTimeField, StringField, UInt64Field
from .db import CLUSTER_NAME, Model, DistributedModel


class Recharges(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    recharge_id = StringField()
    action = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'recharge_id'))


class RechargesDist(Recharges, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
