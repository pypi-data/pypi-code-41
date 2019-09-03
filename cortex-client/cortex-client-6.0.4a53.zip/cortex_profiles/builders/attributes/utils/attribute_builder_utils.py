import uuid
from functools import wraps
from typing import Callable
from typing import List, Optional, Any, Union

import attr
import pandas as pd
import pydash

from cortex_profiles import utils, utils_for_dfs
from cortex_profiles.types.attribute_values import CounterAttributeValue
from cortex_profiles.types.attribute_values import DimensionalAttributeValue, Dimension
from cortex_profiles.types.attributes import ObservedProfileAttribute, ProfileAttribute

from cortex_profiles.utils_for_dfs import df_to_records


def derive_attributes_from_df(
        df:pd.DataFrame,
        attribute_key_pattern:str,
        attribute_class:type,
        attribute_value_constructor:Callable[[pd.DataFrame, dict], DimensionalAttributeValue],
        additional_identifiers:Optional[dict]=None
    ) -> List[ProfileAttribute]:
    return [
        attribute_class(
            id=str(uuid.uuid4()),
            attributeKey=attribute_key_pattern.format(**r),
            profileId=str(r["profileId"]),
            createdAt=utils.utc_timestamp(),
            attributeValue=attribute_value_constructor(r),
        )
        for r in map(lambda x: pydash.merge(additional_identifiers or {}, x), df_to_records(df))
    ]

def _derive_attributes_from_groups_in_df(
        grouped_df:pd.DataFrame,
        group_id_keys:List[str],
        group_id_values:List[Any],
        attribute_key_pattern:str,
        attribute_value_constructor:Callable[[pd.DataFrame, dict], DimensionalAttributeValue],
        attribute_class:type,
        additional_identifiers:Optional[dict]=None,
    ) -> ObservedProfileAttribute:
    if grouped_df.empty:
        return None
    assert "profileId" in grouped_df.columns, "ProfileId must be in dataframe ..."
    identifier = dict(zip(group_id_keys, group_id_values))
    identifier = identifier if not additional_identifiers else pydash.merge(identifier, additional_identifiers)
    return attribute_class(
        id=str(uuid.uuid4()),
        attributeKey=attribute_key_pattern.format(**identifier),
        profileId=str(identifier["profileId"]),
        createdAt=utils.utc_timestamp(),
        attributeValue=attribute_value_constructor(grouped_df, identifier),
    )


def derive_attributes_from_grouped_df(
        grouped_df:pd.DataFrame,
        attribute_identifiers: List[str],
        attribute_key_pattern:str,
        attribute_class:type,
        attribute_value_constructor:Callable[[pd.DataFrame, dict], DimensionalAttributeValue],
        additional_identifiers:Optional[dict]=None
    ) -> List[ObservedProfileAttribute]:
    """
    Builds attributes by grouping dataframes by the :param attribute_identifiers: and using each of the grouped
        dataframes to constuct the appropriate attribute value.

    :param df: The dataframe to generate dimensional attributes from
    :param attribute_identifiers: The list of identifiers to group by when generating dimensional attributes from the dataframe ...
    :param attribute_key_pattern: The string template of the name of the attribute key that gets populated form the
                                  unique identifier of the grouping that gets transformed into the dimensional attribute.
    :param attribute_class: The class to use for the attribute ...
    :param attribute_value_constructor: The constructor to construct the attribute value from the grouped dataframe.
    :param additional_identifiers:
    :return:
    """
    return [
        _derive_attributes_from_groups_in_df(
            gdf,
            attribute_identifiers,
            list(gid),
            attribute_key_pattern,
            attribute_value_constructor,
            attribute_class,
            additional_identifiers
        )
        for gid, gdf in grouped_df
    ]


def derive_attributes_from_groups_in_df(
        df:pd.DataFrame,
        attribute_identifiers:List[str],
        attribute_key_pattern:str,
        attribute_class:type,
        attribute_value_constructor:Callable[[pd.DataFrame, dict], DimensionalAttributeValue],
        additional_identifiers:Optional[dict]=None
    ) -> List[ObservedProfileAttribute]:
    """
    Builds attributes by grouping dataframes by the :param attribute_identifiers: and using each of the grouped
        dataframes to constuct the appropriate attribute value.

    :param df: The dataframe to generate dimensional attributes from
    :param attribute_identifiers: The list of identifiers to group by when generating dimensional attributes from the dataframe ...
    :param attribute_key_pattern: The string template of the name of the attribute key that gets populated form the
                                  unique identifier of the grouping that gets transformed into the dimensional attribute.
    :param attribute_class: The class to use for the attribute ...
    :param attribute_value_constructor: The constructor to construct the attribute value from the grouped dataframe.
    :param additional_identifiers:
    :return:
    """
    return derive_attributes_from_grouped_df(
        df.groupby(attribute_identifiers, as_index=False),
        attribute_identifiers,
        attribute_key_pattern,
        attribute_class,
        attribute_value_constructor,
        additional_identifiers,
    )


def simple_dimensional_attribute_value_constructor(
        context_of_dimension_id:str,
        context_of_dimension_value:Union[type, str],
        column_for_dimension_id:str,
        column_for_dimension_value:str,
        dimension_value_constructor:Optional[Callable]=None
    ):
    """
    Responsible for providing a constuctor that is capable of building a dimensional attribute value ...

    :param context_of_dimension_id: The context to use for the dimensionId.
    :param context_of_dimension_value: The context to use for the dimensionValue.
    :param column_for_dimension_id: The column from the group to use as the dimensionId.
    :param column_for_dimension_value: The column from the group to use as the dimensionValue.
    :return:
    """

    def attribute_value_factory_method(grouped_df:pd.DataFrame, identifiers:dict):
        """
        Constucts an Dimensional Attribute Value given a grouped dataframe and the identifiers of the group
        :param grouped_df:
        :param identifiers:
        :return:
        """
        return DimensionalAttributeValue(
            contextOfDimension=context_of_dimension_id.format(**identifiers),
            # contextOfDimension=identifiers[context_of_dimension_id] if context_of_dimension_id in identifiers else context_of_dimension_id,
            contextOfDimensionValue=attr.fields(context_of_dimension_value).context.default if not isinstance(context_of_dimension_value, str) else context_of_dimension_value,
            value=list(sorted(
                [
                    Dimension(dimensionId=x, dimensionValue=y if dimension_value_constructor is None else dimension_value_constructor(y))
                    for x, y in utils_for_dfs.df_to_tuples(grouped_df, [column_for_dimension_id, column_for_dimension_value])
                ],
                key=lambda d: d.dimensionValue
            ))
        )
    return attribute_value_factory_method


def simple_counter_attribute_value_constructor(
        column_of_counter:str,
        attribute_value_class:Union[type, Callable]=CounterAttributeValue,
        counter_deriver=lambda column: sum(column)
    ):
    """
    Responsible for providing a constructor that is capable of building a counter attribute from a grouped dataframe ...

    :param column_of_counter:
    :param attribute_class:
    :return:
    """
    def attribute_value_factory_method(grouped_df:pd.DataFrame, identifiers:dict):
        """
        Constructs an Dimensional Attribute Value given a grouped DataFrame and the identifiers of the group
        :param grouped_df:
        :param identifiers:
        :return:
        """
        value = counter_deriver(grouped_df[column_of_counter])
        return attribute_value_class(value=value) if isinstance(attribute_value_class, type) else attribute_value_class(value)
    return attribute_value_factory_method


def simple_attribute_value_selector_constructor(
        column_to_select_value_from:str,
        attribute_value_class:Union[type, Callable]=CounterAttributeValue
    ):
    """
    Responsible for providing a constructor that is capable of building a counter attribute from a grouped dataframe ...

    :param column_of_counter:
    :param attribute_class:
    :return:
    """
    def attribute_value_factory_method(grouped_df:pd.DataFrame, identifiers:dict):
        """
        Constructs an Dimensional Attribute Value given a grouped DataFrame and the identifiers of the group
        :param grouped_df:
        :param identifiers:
        :return:
        """
        value = utils.head(list(grouped_df[column_to_select_value_from]))
        return attribute_value_class(value=value) if isinstance(attribute_value_class, type) else attribute_value_class(value)
    return attribute_value_factory_method


def derive_quantile_config_for_column(df:pd.DataFrame, column_name:str, quantile_config:dict) -> pd.Series:
    return {
        key: list(map(lambda x: df[column_name].quantile(x), values)) for key, values in quantile_config.items()
    }


def determine_bucket_from_quartile_config(value:object, config:dict) -> str:
    # Taking tail for values on the edge to be more generous
    return [key for key, values in config.items() if (value >= values[0] and value <= values[1])][-1]


def high_med_low_bucket(df:pd.DataFrame, column_name:str, quantile_config:dict) -> pd.Series:
    return df[column_name].map(lambda x: determine_bucket_from_quartile_config(x, quantile_config))


def state_modifier(result_factory:Callable, state_updater:Callable[[Any, Any], Any]):
    def inner_decorator(f_to_wrap:Callable):
        @wraps(result_factory)
        def f_that_gets_called(*args, **kwargs):
            state_updater(args[0], result_factory(*args[1:], **kwargs))
            return f_to_wrap(args[0])
        return f_that_gets_called
    return inner_decorator


if __name__ == '__main__':
    # print([
    #     (gid, list(gdf["a"]), list(gdf["b"]))
    #     for gid, gdf in pd.DataFrame([{"a":1, "b": 2}]).groupby(["a", "b"])
    # ])

    df = pd.DataFrame([
        {"profileId": "1", "interaction": "like"},
        {"profileId": "1", "interaction": "like"},
        {"profileId": "1", "interaction": "dislike"},
        {"profileId": "1", "interaction": "like"}
    ])

    for attribute in derive_attributes_from_groups_in_df(
        df,
        ["profileId", "interaction"],
        "countOf.interaction[{interaction}]",
        ObservedProfileAttribute,
        lambda grouped_df, identifiers: CounterAttributeValue(value=len(list(grouped_df["interaction"])))
    ):
        print(attribute)

