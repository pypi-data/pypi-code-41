from infi.clickhouse_orm import engines

from .fields import DateField, DateTimeField, JsonStringField, BoolStringField, StringField, UInt64Field, Int64Field
from .db import CLUSTER_NAME, Model, DistributedModel


class ArmyCollectionLog(Model):
    day = DateField()
    profile_id = StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class ArmyCollectionLogDist(ArmyCollectionLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ArmyCollectionStatus(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    monster_id = StringField()
    souls = Int64Field()
    promotes = Int64Field()
    guild_power = Int64Field()
    reborn = Int64Field()
    soul_binding = StringField()
    decks = StringField()
    rarity = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('day', 'profile_id', 'monster_id'))


class ArmyCollectionStatusDist(ArmyCollectionLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class CheaterMarks(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    is_paying = BoolStringField()
    action = StringField()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('profile_id',))


class CheaterMarksDist(CheaterMarks, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ForeignId(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    appsflyer_id = StringField()
    advertising_id = StringField()
    idfa = StringField()
    appsflyer_data = StringField()
    utm_data = StringField()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('profile_id'))


class ForeignIdDist(ForeignId, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class PetDynamics(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    action = StringField()
    match_id = StringField()
    pet_id = UInt64Field()
    pet_promote = UInt64Field()
    pet_souls = Int64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'pet_id'))


class PetDynamicsDist(PetDynamics, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class HuntDynamics(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    action = StringField()
    hunt_id = StringField()
    quest_id = StringField()
    price_resource_type = StringField()
    price_amount = Int64Field()
    reward_id = StringField()
    reward_amount = Int64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'action'))


class HuntDynamicsDist(HuntDynamics, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ProfileDynamics(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    occurrence_type = StringField()
    occurrence_value = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'occurrence_type'))


class ProfileDynamicsDist(ProfileDynamics, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ProfileStatus(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    env = StringField()
    platform_id = StringField()
    player_country = StringField()
    install_timestamp = DateTimeField()
    appsflyer_id = StringField()
    is_paying = BoolStringField()
    is_cheater = BoolStringField()
    is_qa = BoolStringField()
    league = UInt64Field(default=32)
    rank = UInt64Field()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('profile_id',))


class ProfileStatusDist(ProfileStatus, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Registers(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    env = StringField()
    player_country = StringField()
    utm_campaign = StringField()
    utm_medium = StringField()
    utm_source = StringField()
    utm_full = StringField()
    platform_id = StringField()
    advertising_id = StringField() # MP only

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'platform_id'))


class RegistersDist(Registers, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ResourcesLog(Model):
    day = DateField()
    profile_id = StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class ResourcesLogDist(ResourcesLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Sessions(Model):
    day = DateField()
    event_type = StringField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    env = StringField()
    device_id = StringField()
    player_country = StringField()
    platform_id = StringField()
    client_ip = StringField()
    login_id = StringField()
    request_id = StringField()
    forced_session = BoolStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'event_type'))


class SessionsDist(Sessions, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class StartExperience(Model):
    day = DateField()
    created_on = DateTimeField()
    user_id = StringField()
    profile_id = StringField()
    event = StringField()
    utm_campaign = StringField()
    utm_content = StringField()
    description = StringField()
    seconds = StringField()
    new_user = StringField()
    referer = StringField()
    user_agent = StringField()

    engine = engines.ReplacingMergeTree(partition_key=('day',), order_by=('user_id',))


class StartExperienceDist(StartExperience, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
