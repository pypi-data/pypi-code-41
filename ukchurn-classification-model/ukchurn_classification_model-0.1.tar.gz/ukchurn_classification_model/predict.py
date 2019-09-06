# libs
import pandas as pd
pd.set_option('display.max_columns', None)

# packages
from ukchurn_classification_model.data_management.pipeline_management import load_pipeline
from ukchurn_classification_model.data_management.data_validation import validate_inputs
from ukchurn_classification_model.config import config


_churn_model_pipeline = load_pipeline(file_name=config.PIPELINE_NAME)


def predict(*, input_data: pd.DataFrame):
    """Make a prediction using a saved model pipeline.

    Args:
        input_data: Array of model prediction inputs.

    Returns:
        Predictions for each input row, as well as the model version.
    """

    # import data as DataFrame
    data = pd.DataFrame(input_data)

    # checks and drops NaN rows not seen during model training process
    validated_data = validate_inputs(input_data=data[config.FEATURES])

    # predict binary result
    prediction = _churn_model_pipeline.predict(validated_data)

    # predict probability output
    proba_prediction = _churn_model_pipeline.predict_proba(validated_data)
    probability_0 = []
    probability_1 = []
    for row in range(len(proba_prediction)):
        probability_0.append(proba_prediction[row][0])
        probability_1.append(proba_prediction[row][1])


    # final output
    predictions = pd.DataFrame(
        {'probability_0': probability_0, 'probability_1': probability_1, 'flag_churn': prediction},
        columns=['probability_0', 'probability_1', 'flag_churn']
    )

    return predictions
