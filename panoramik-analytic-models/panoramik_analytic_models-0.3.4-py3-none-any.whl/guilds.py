from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, BoolStringField, StringField, UInt64Field
from .db import CLUSTER_NAME, Model, DistributedModel


class GuildshopItem(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    guild_id = UInt64Field()
    item_id = UInt64Field()
    item_level = UInt64Field()
    league = UInt64Field(default=32)

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'guild_id'))


class GuildshopItemDist(GuildshopItem, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class TroopsHiding(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    guild_id = UInt64Field()
    guild_name = StringField()
    war_id = UInt64Field()
    room_number = UInt64Field()
    spent_gems = UInt64Field()
    cell_x = UInt64Field()
    cell_y = UInt64Field()
    hidden = BoolStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'war_id', 'room_number'))


class TroopsHidingDist(TroopsHiding, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
