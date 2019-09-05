import pandas as pd
from typing import Dict, Any
from collections import defaultdict
import math


def analyze_df_column(
    df: pd.DataFrame,
    column_name: str,
    categorial_detection_treshold: float = 0.05,
):
    types: Dict[type, int] = defaultdict(lambda: 0)
    contains_duplicates: bool = False
    contains_nan: bool = False
    values_distribution: Dict[Any, int] = defaultdict(lambda: 0)
    is_categorical: bool = False
    is_mixed_type: bool = False
    length = 0

    for value in df[column_name]:
        types[type(value)] += 1

        if not contains_nan and isinstance(value, float):
            contains_nan = math.isnan(value)

        if value in values_distribution:
            contains_duplicates += 1

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
        "types_distribution": {str(k): v / length for k, v in types.items()},
        "is_categorical": is_categorical,
    }

    if is_categorical:
        result["categories_distribution"] = (
            {str(k): v / length for k, v in values_distribution.items()},
        )

    return result
