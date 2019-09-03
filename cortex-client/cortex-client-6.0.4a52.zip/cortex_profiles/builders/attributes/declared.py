from typing import List, Optional, Union, Callable

import pandas as pd

from cortex_profiles import utils, utils_for_dfs
from cortex_profiles.builders.attributes.utils.attribute_builder_utils import state_modifier
from cortex_profiles.types.attribute_values import IntegerAttributeValue, DecimalAttributeValue, StringAttributeValue, \
    BooleanAttributeValue, ListAttributeValue, DimensionalAttributeValue, Dimension
from cortex_profiles.types.attributes import DeclaredProfileAttribute


def dimensional_from_dict(d:dict, contextOfDimension:str, contextOfDimensionValue:str, key_modifier=lambda x:x, value_modifier=lambda x:x):
    d = DimensionalAttributeValue(
        value=[
            Dimension(k, v)
            for k, v in d.items()
        ],
        contextOfDimension=contextOfDimension,
        contextOfDimensionValue=contextOfDimensionValue
    )
    return d


def built_in_attribute_value_constructor(value:Union[int, float, str, bool, list]) -> Union[IntegerAttributeValue,
                                                                                            DecimalAttributeValue,
                                                                                            StringAttributeValue,
                                                                                            BooleanAttributeValue,
                                                                                            ListAttributeValue,
                                                                                            StringAttributeValue]:
    if isinstance(value, int):
        return IntegerAttributeValue(value=value)
    if isinstance(value, float):
        return DecimalAttributeValue(value=value)
    if isinstance(value, str):
        return StringAttributeValue(value=value)
    if isinstance(value, bool):
        return BooleanAttributeValue(value=value)
    if isinstance(value, list):
        return ListAttributeValue(value=value)


def derive_declared_attributes_from_key_value_df(
        df:pd.DataFrame,
        profile_id_column:str="profileId",
        key_column:str="key",
        value_column:str="value",
        time_column:Optional[str]=None,
        attribute_value_constructor:Union[type, Callable]=built_in_attribute_value_constructor
    ) -> List[DeclaredProfileAttribute]:
    """
    Derives attributes from a dataframe that is structured as follows ....
    >>> import pandas as pd
    >>> df = pd.DataFrame([
    >>>    {"profileId": "p1", "key": "profile.name", "value": "Jack"},
    >>>    {"profileId": "p1", "key": "profile.age", "value": 25},
    >>>    {"profileId": "p2", "key": "profile.name", "value": "Jill"},
    >>>    {"profileId": "p2", "key": "profile.age", "value": 26},
    >>> ])

    :param df: The data frame with all of the attributes ...
    :param profile_id_column: The column with the profile Id
    :param key_column: The column containing the key we want to use as the attributeKey
    :param value_column: The column that contains the value of the attribute
    :param attribute_value_constructor: The constructor to construct the attribute Value Class with the Value column in the df.
    :return: List of Declared Attributes derived from the dataframe.
    """
    return [
        DeclaredProfileAttribute(
            id=utils.unique_id(),
            attributeKey=rec[key_column],
            profileId=str(rec[profile_id_column]),
            createdAt=utils.utc_timestamp() if time_column is None else rec[time_column],
            attributeValue=attribute_value_constructor(rec[value_column]),
        )
        for rec in utils_for_dfs.df_to_records(df)
    ]


def derive_declared_attributes_from_value_only_df(
        declarations:pd.DataFrame,
        value_column:str,
        profile_id_column:str="profileId",
        key:Optional[str]=None,
        time_column:Optional[str]=None,
        attribute_value_constructor:Union[type, Callable]=built_in_attribute_value_constructor
    ) -> List[DeclaredProfileAttribute]:
    """
    Derives attributes from a dataframe that is structured as follows ....
    >>> import pandas as pd
    >>> df = pd.DataFrame([
    >>>     {"profileId": "p3", "name": "Adam", "age": 45},
    >>>     {"profileId": "p4", "name": "Eve", "age": 46},
    >>> ])

    :param df: The data frame with all of the attributes ...
    :param profile_id_column: The column with the profile Id
    :param key: The key to use as the attribute key ... if no key is specified, the name of the value column is used ...
    :param value_column: The column that contains the value of the attribute
    :param attribute_value_constructor: The constructor to construct the Attribute Value Class from the value
                                  stored in the value column for a particular attribute.
    :return: List of Declared Attributes derived from the dataframe.
    """
    return [
        DeclaredProfileAttribute(
            id=utils.unique_id(),
            attributeKey=key if key else value_column,
            profileId=str(rec[profile_id_column]),
            createdAt=utils.utc_timestamp() if time_column is None else rec[time_column],
            attributeValue=attribute_value_constructor(rec[value_column])
        )
        for rec in utils_for_dfs.df_to_records(declarations)
    ]


class DeclaredAttributesBuilder(object):
    def __init__(self):
        self.attributes = [ ]

    @state_modifier(derive_declared_attributes_from_key_value_df, (lambda self, results: self.attributes.extend(results)))
    def append_attributes_from_kv_df(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_key_value_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self

    @state_modifier(derive_declared_attributes_from_value_only_df, (lambda self, results: self.attributes.extend(results)))
    def append_attributes_from_column_in_df(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_value_only_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self

    def get(self) -> List[DeclaredProfileAttribute]:
        return self.attributes


if __name__ == '__main__':

    # TODO ... turn this into an example ...

    kv_df = pd.DataFrame([
       {"profileId": "p1", "key": "profile.name", "value": "Jack"},
       {"profileId": "p1", "key": "profile.age", "value": 25},
       {"profileId": "p2", "key": "profile.name", "value": "Jill"},
       {"profileId": "p2", "key": "profile.age", "value": 26},
    ])

    value_only_df = pd.DataFrame([
        {"profileId": "p3", "name": "Adam", "age": 45},
        {"profileId": "p4", "name": "Eve", "age": 46},
    ])

    attributes = (
        DeclaredAttributesBuilder()
            .append_attributes_from_kv_df(kv_df)
            .append_attributes_from_column_in_df(value_only_df, key="profile.name", value_column="name")
            .append_attributes_from_column_in_df(value_only_df, key="profile.age", value_column="age")
            .get()
    )

    print("{} total attributes generated.".format(len(attributes)))
    for attribute in attributes:
        print(attribute)

    # print(DeclaredAttributesBuilder().append_attributes_from_kv_df.__doc__)
    # print(DeclaredAttributesBuilder().append_attributes_from_column_in_df.__doc__)
