# libs
import pandas as pd

# packages
from ukchurn_classification_model.predict import predict
from ukchurn_classification_model.config import config


def test_make_single_prediction():
    # Given
    test_data = pd.read_csv(filepath_or_buffer=config.TESTING_DATA_FILE)
    single_test_input = test_data[0:5]

    # When
    prediction = predict(input_data=single_test_input)

    # Then
    # print(prediction)
    assert prediction is not None


def test_make_multiple_prediction():
    # Given
    test_data = pd.read_csv(filepath_or_buffer=config.TESTING_DATA_FILE)

    # When
    prediction = predict(input_data=test_data)

    # Then
    assert prediction is not None
