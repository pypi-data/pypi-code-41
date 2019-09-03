from typing import List, Tuple, Optional

import pandas as pd

from cortex_profiles.builders.attributes import implicit
from cortex_profiles.schemas.schemas import PROFILE_TYPES
from cortex_profiles.synthetic.attribute_values import AttributeValueProvider
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic.insights import InsightsProvider
from cortex_profiles.synthetic.interactions import InteractionsProvider
from cortex_profiles.synthetic.sessions import SessionsProvider
from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.types.attribute_values import BaseAttributeValue
from cortex_profiles.types.attributes import ProfileAttribute, DeclaredProfileAttribute, InferredProfileAttribute, \
    ObservedProfileAttribute, AssignedProfileAttribute
from cortex_profiles.types.insights import Insight
from cortex_profiles.types.interactions import Session, InsightInteractionEvent
from cortex_profiles.types.profiles import ProfileAttributeMapping
from cortex_profiles.utils import unique_id, utc_timestamp
from cortex_profiles.utils_for_dfs import list_of_attrs_to_df

value = ["duration", "count", "total", "distribution"]
app_specififity = ["app-specific", "app-agnostic"]
algo_specififity = ["algo-specific", "algo-agnostic",]
timeframe = ["{}{}".format(x, y) for x in range(0, 6) for y in ["week", "month", "year"]] + ["recent", "eternal"]
purpose = ["insight-interaction", "app-activity", "app-preferences", "algo-preferences", "user-declarations"]


class AttributeProvider(BaseProviderWithDependencies):

    def __init__(self, *args, concept_universe: List[dict]=None, **kwargs):
        super(AttributeProvider, self).__init__(*args, **kwargs)
        self.conceptsToMakeEntityEventsFor = [x.get("context") for x in concept_universe or [] if x.get("context")]

    def dependencies(self) -> List[type]:
        return [
            InsightsProvider,
            InteractionsProvider,
            SessionsProvider,
            AttributeValueProvider,
            TenantProvider
        ]

    def data_to_build_single_profile(self, profileId:str=None, max_sessions=10, max_insights=100) -> Tuple[str, List[Session], List[Insight], List[InsightInteractionEvent]]:
        profileId = profileId if profileId else self.fake.profileId()
        sessions = self.fake.sessions(profileId=profileId, max_sessions=max_sessions)
        insights = self.fake.insights(profileId=profileId, max_insights=max_insights)
        interactions = self.fake.interactions(profileId, sessions, insights)
        return (profileId, sessions, insights, interactions)

    def dfs_to_build_single_profile(self, profileId:str=None) -> Tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        profileId, sessions, insights, interactions = self.data_to_build_single_profile(profileId=profileId)
        return (
            profileId, list_of_attrs_to_df(sessions), list_of_attrs_to_df(insights), list_of_attrs_to_df(interactions)
        )

    def attributes_for_single_profile(self, profileId:str=None) -> List[ProfileAttribute]:
        """
        This returns a list of synthesized implicit attributes that cortex is capable of generating for profiles.
        :param profileId:
        :return:
        """
        (profileId, sessions_df, insights_df, interactions_df) = self.dfs_to_build_single_profile(profileId=profileId)
        return implicit.derive_implicit_attributes_from_insight_interactions(insights_df, interactions_df, sessions_df, self.conceptsToMakeEntityEventsFor) + [
            implicit.derive_implicit_profile_type_attribute(profileId, self.random_subset_of_list(PROFILE_TYPES.values()))
        ]

    def unique_attribute_key(self):
        return "value[{value}].app_specififity[{app_specififity}].algo_specififity[{algo_specififity}].timeframe[{timeframe}].purpose[{purpose}]".format(
            value=self.fake.random.choice(value),
            app_specififity=self.fake.random.choice(app_specififity),
            algo_specififity=self.fake.random.choice(algo_specififity),
            timeframe=self.fake.random.choice(timeframe),
            purpose=self.fake.random.choice(purpose)
        )

    def inferred_attribute(self, attributeKey:Optional[str]=None, attribute_value:Optional[BaseAttributeValue]=None) -> InferredProfileAttribute:
        return self.attribute(attributeKey=attributeKey, attribute_class=InferredProfileAttribute, attribute_value=attribute_value)

    def declared_attribute(self, attributeKey:Optional[str]=None, attribute_value:Optional[BaseAttributeValue]=None) -> DeclaredProfileAttribute:
        return self.attribute(attributeKey=attributeKey, attribute_class=DeclaredProfileAttribute, attribute_value=attribute_value)

    def observed_attribute(self, attributeKey:Optional[str]=None, attribute_value:Optional[BaseAttributeValue]=None) -> ObservedProfileAttribute:
        return self.attribute(attributeKey=attributeKey, attribute_class=ObservedProfileAttribute, attribute_value=attribute_value)

    def assigned_attribute(self, attributeKey:Optional[str]=None, attribute_value:Optional[BaseAttributeValue]=None) -> AssignedProfileAttribute:
        return self.attribute(attributeKey=attributeKey, attribute_class=AssignedProfileAttribute, attribute_value=attribute_value)

    def attribute(self, attributeKey:Optional[str]=None, attribute_class:Optional[ProfileAttribute]=None, attribute_value:Optional[BaseAttributeValue]=None) -> ProfileAttribute:
        attr_key = attributeKey if attributeKey else self.unique_attribute_key()
        attr_class = attribute_class if attribute_class else self.fake.random.choice(
            [DeclaredProfileAttribute, InferredProfileAttribute, ObservedProfileAttribute, AssignedProfileAttribute]
        )
        attr_value = attribute_value if attribute_value else self.fake.attribute_value()
        return attr_class(
            id=unique_id(),
            profileId=self.fake.profileId(),
            createdAt=utc_timestamp(),
            attributeKey=attr_key,
            attributeValue=attr_value,
            tenantId=self.fake.tenantId(),
            environmentId=self.fake.environmentId(),
            onLatestProfile=True,
            commits=[unique_id() for x in self.fake.range(0, 10)]
        )

    def attributes(self, limit=100) -> List[ProfileAttribute]:
        return [
            self.attribute() for x in self.fake.range(0, limit)
        ]

    def attribute_mappings(self, limit=100) -> List[ProfileAttributeMapping]:
        return [
            ProfileAttributeMapping(
                attributeKey=x.attributeKey,
                attributeId=x.id
            )
            for x in self.attributes(limit)
        ]


def test_attr_provider(f):
    for x in range(0, 100):
        print(x, f.attributes_for_single_profile("1"))


def generate_attribute_samples(synthesizer) -> dict:
    attributes = {
        "inferred_attribute": synthesizer.inferred_attribute("profile.interestIn.company", synthesizer.weighted_value()),
        "declared_attribute": synthesizer.declared_attribute("profile.favorite_color", synthesizer.string_value()),
        "observed_attribute": synthesizer.observed_attribute("profile.likes.insights.relatedToMicrosoft",
                                                       synthesizer.counter_value()),
        "assigned_attribute": synthesizer.assigned_attribute("profile.types", synthesizer.profile_type_value()),
    }
    return attributes


if __name__ == '__main__':
    import os
    import json
    from cortex_profiles.synthetic import create_profile_synthesizer
    for name, attribute in generate_attribute_samples(create_profile_synthesizer()).items():
        with open("{}/../../samples/attributes/{}.json".format(os.path.dirname(__file__), name), "w") as fh:
            json.dump(dict(attribute), fh, indent=4)
