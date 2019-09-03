from typing import List, Optional, Any

from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.types.attribute_values import \
    Dimension, RelationshipAttributeValue, NumericAttributeValue, PercentileAttributeValue, \
    PercentageAttributeValue, CounterAttributeValue, TotalAttributeValue, \
    DimensionalAttributeValue, StringAttributeValue, DecimalAttributeValue, IntegerAttributeValue, \
    BooleanAttributeValue, ListAttributeValue, WeightedAttributeValue, EntityAttributeValue
    # ObjectAttributeValue, AverageAttributeValue, PrimitiveAttributeValue, ConceptAttributeValue

from cortex_profiles.utils import unique_id

# Add this to the configurable universe ...
PROFILE_TYPES = [
    "cortex/end-user-profile",
    "cortex/investor-profile",
    "cortex/medical-client-profile",
    "cortex/shopper-profile"
]

class AttributeValueProvider(BaseProviderWithDependencies):

    # def __init__(self, *args, **kwargs):
    #     super(AttributeValueProvider, self).__init__(*args, **kwargs)
    #     self.fake = args[0]

    def dependencies(self) -> List[type]:
        return [
            TenantProvider
        ]

    def dimensional_value(self, max_dimensions=7) -> DimensionalAttributeValue:
        dimensions = [
            Dimension(dimensionId=unique_id(), dimensionValue=self.fake.random.randint(0, 100))
            for x in self.fake.range(0, max_dimensions)
        ]
        return DimensionalAttributeValue(
            value=dimensions,
            contextOfDimension = self.fake.random.choice(list(CONTEXTS.keys())),
            contextOfDimensionValue = "int"   # What type is the value associated with the dimension?
        )

    def string_value(self) -> StringAttributeValue:
        return StringAttributeValue(value=self.fake.color_name())

    def integer_value(self) -> IntegerAttributeValue:
        return IntegerAttributeValue(value=self.fake.random.randint(0, 100))

    def decimal_value(self) -> DecimalAttributeValue:
        return DecimalAttributeValue(value=self.fake.random.randint(0, 100) / 0.1)

    def boolean_value(self) -> BooleanAttributeValue:
        return BooleanAttributeValue(value=self.fake.random.choice([True, False]))


    def list_value(self) -> ListAttributeValue:
        return ListAttributeValue(value=self.fake.random_subset_of_list(list(
            set(list(map(lambda x: x(), [self.fake.color_name]*10)))
        )))

    # def object_value(self) -> ObjectAttributeValue:
    #     return ObjectAttributeValue(value=dict(zip(["favorite_color"], [self.fake.color_name()])))
    #
    # def primitive_value(self) -> PrimitiveAttributeValue:
    #     return PrimitiveAttributeValue(
    #         value=self.fake.random.choice([
    #             self.string_value,
    #             self.boolean_value,
    #             self.integer_value,
    #             self.decimal_value,
    #         ])().value
    #     )
    #
    # def average_value(self) -> AverageAttributeValue:
    #     return AverageAttributeValue(value=self.fake.random.randint(0, 1000) * 0.98)
    #
    # def concept_value(self) -> ConceptAttributeValue:
    #     return ConceptAttributeValue(
    #         value=unique_id()
    #     )

    def percentile_value(self) -> PercentileAttributeValue:
        return PercentileAttributeValue(value=min(self.fake.random.randint(0, 100) * 0.98, 100))

    def percentage_value(self) -> PercentageAttributeValue:
        return PercentageAttributeValue(value=min(self.fake.random.randint(0, 100) * 0.98, 100))


    def numeric_value(self) -> NumericAttributeValue:
        return NumericAttributeValue(value=self.fake.random.choice([int, float])(self.fake.random.randint(0,100) * 0.123))

    def counter_value(self) -> CounterAttributeValue:
        return CounterAttributeValue(value=self.fake.random.randint(0, 2500))

    def total_value(self) -> TotalAttributeValue:
        return TotalAttributeValue(value=self.numeric_value().value)

    def relationship_value(self) -> RelationshipAttributeValue:
        return RelationshipAttributeValue(
            value=unique_id(),
            relatedConceptType=self.fake.random.choice(list(CONTEXTS.keys())),
            relationshipType="cortex/likes",
            relationshipTitle="Likes",
            relatedConceptTitle=self.fake.company(),
            relationshipProperties={}
        )


    def weighted_value(self, value:Optional[Any]=None) -> WeightedAttributeValue:
        return WeightedAttributeValue(
            value=value if value is not None else self.fake.company(),
            weight=self.fake.random.randint(0,100) / 100.00
        )

    def entity_value(self, value:Optional[Any]=None) -> EntityAttributeValue:
        return EntityAttributeValue(
            value=value if value is not None else {
                "company": self.fake.company(),
                "employees": self.fake.random.randint(1,1000*1000)
            }
        )

    def profile_type_value(self) -> ListAttributeValue:
        return ListAttributeValue(
            value=self.fake.random_subset_of_list([
                PROFILE_TYPES
            ])
        )

    def attribute_value(self):
        return self.fake.random.choice([
            self.dimensional_value,
            # self.object_value,
            self.relationship_value,
            self.numeric_value,
            self.percentage_value,
            self.percentile_value,
            # self.average_value,
            self.counter_value,
            self.total_value,
            self.profile_type_value
        ])()


def test_attr_value_provider(f):
    # print(f.attributes_for_single_profile())
    for x in range(0, 100):
        print(f.attribute_value())


def generate_attribute_value_samples(synthesizer) -> dict:
    return {
        "string_value": synthesizer.string_value(),
        "integer_value": synthesizer.integer_value(),
        "decimal_value": synthesizer.decimal_value(),
        "dimensional_value": synthesizer.dimensional_value(),
        "boolean_value": synthesizer.boolean_value(),
        # "object_value": synthesizer.object_value(),
        "list_value": synthesizer.list_value(),
        # "primitive_value": synthesizer.primitive_value(),
        "percentile_value": synthesizer.percentile_value(),
        "percentage_value": synthesizer.percentage_value(),
        # "average_value": synthesizer.average_value(),
        "numeric_value": synthesizer.numeric_value(),
        "counter_value": synthesizer.counter_value(),
        "total_value": synthesizer.total_value(),
        "relationship_value": synthesizer.relationship_value(),
        # "concept_value": synthesizer.concept_value(),
        "weighted_value": synthesizer.weighted_value(),
        "entity_value": synthesizer.entity_value()
    }


if __name__ == "__main__":
    import json
    import os
    from cortex_profiles.synthetic import create_profile_synthesizer
    import attr
    for name, attribute_value in generate_attribute_value_samples(create_profile_synthesizer()).items():
        with open("{}/../../samples/attribute_values/{}.json".format(os.path.dirname(__file__), name), "w") as fh:
            json.dump(attr.asdict(attribute_value), fh, indent=4)
