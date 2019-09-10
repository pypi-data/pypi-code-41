# libs
import pandas as pd

# packages
from ukchurn_classification_model.config import config


def validate_inputs(input_data: pd.DataFrame) -> pd.DataFrame:
    """Check model inputs for unprocessable values"""

    validated_data = input_data.copy()

    # check for numerical variables with NA not seen during training
    if input_data[config.NUMERICAL_NA_NOT_ALLOWED].isnull().any().any():
        validated_data = validated_data.dropna(
            axis=0, subset=config.NUMERICAL_NA_NOT_ALLOWED)

    # check for categorical variables with NA not seen during training
    if input_data[config.CATEGORICAL_NA_NOT_ALLOWED].isnull().any().any():
        validated_data = validated_data.dropna(
            axis=0, subset=config.CATEGORICAL_NA_NOT_ALLOWED)

    return validated_data