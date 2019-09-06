import numpy as np
import pandas as pd
from typing import Dict, Any
from collections import defaultdict
import math


def analyze_df_column(
    df: pd.DataFrame,
    column_name: str,
    categorial_detection_treshold: float = 0.05,
) -> Dict[str, Any]:
    types: Dict[type, int] = defaultdict(lambda: 0)
    contains_duplicates: bool = False
    contains_nan: bool = False
    values_distribution: Dict[Any, int] = defaultdict(lambda: 0)
    is_categorical: bool = False
    is_mixed_type: bool = False
    length = 0

    for value in df[column_name]:
        types[type(value)] += 1

        if not contains_nan and isinstance(value, (float, np.float64)):
            contains_nan = math.isnan(value)

        if value in values_distribution:
            contains_duplicates = True

        values_distribution[value] += 1
        length += 1

    if (
        len(values_distribution) / df[column_name].shape[0]
    ) <= categorial_detection_treshold:
        is_categorical = True

    if len(types) > 1:
        is_mixed_type = True

    result = {
        "length": length,
        "number_of_different_values": len(values_distribution),
        "contains_duplicates": contains_duplicates,
        "contains_nan": contains_nan,
        "is_mixed_type": is_mixed_type,
        "types_distribution": {
            k.__name__: v / length for k, v in types.items()
        },
        "is_categorical": is_categorical,
        "is_categorical_choice": f"{len(values_distribution) / df[column_name].shape[0]} < {categorial_detection_treshold}",
    }

    if is_categorical:
        result["categories_distribution"] = (
            {str(k): v / length for k, v in values_distribution.items()},
        )

    description = df[column_name].describe()
    for col in ["mean", "std", "min", "25%", "50%", "75%", "max"]:
        if col in description:
            result[col] = description[col]

    return result


def analyze_text_column(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
    for text in df[column_name]:
        text.lower()
