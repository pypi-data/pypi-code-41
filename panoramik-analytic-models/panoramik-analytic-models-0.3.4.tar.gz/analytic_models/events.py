from infi.clickhouse_orm import engines

from .fields import DateField, DateTimeField, StringField, UInt64Field, UInt32Field
from .db import CLUSTER_NAME, Model, DistributedModel


class EventInfoChanges(Model):
    day = DateField()
    created_on = DateTimeField()
    event_id = StringField()
    event_name = StringField()
    event_type = StringField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    event_scale = UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'event_id',))


class EventInfoChangesDist(EventInfoChanges, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventQuestCompletion(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    league = UInt64Field(default=32)
    event_id = UInt64Field()
    quest_id = UInt64Field()
    stars = UInt64Field()
    chapter = UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class EventQuestCompletionDist(EventQuestCompletion, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventStart(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    league = UInt64Field(default=32)
    event_id = UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'event_id'))


class EventStartDist(EventStart, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class MiniEvents(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    action = StringField()
    platform = StringField()
    mini_event_id = UInt64Field()
    parent_id = UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'mini_event_id'))


class MiniEventsDist(MiniEvents, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class QuestChapters(Model):
    day = DateField()
    event_id = UInt64Field()
    chapter_number = UInt32Field()
    chapter_id = UInt32Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('event_id',))


class QuestChaptersDist(QuestChapters, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class QuestIds(Model):
    day = DateField()
    event_id = UInt64Field()
    quest_id = UInt64Field()
    chapter_id = UInt32Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('event_id',))


class QuestIdsDist(QuestIds, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
