# libs
import unittest
import pandas as pd

# packages
from ukchurn_classification_model.predict import predict
from ukchurn_classification_model.config import config


class TestPrediction(unittest.TestCase):

    def setUp(self):
        self.test_data = pd.read_csv(filepath_or_buffer=config.TESTING_DATA_FILE)

    def test_make_single_prediction(self):
        # When
        single_prediction = predict(input_data=self.test_data[0:1])

        # Then
        self.assertIsNotNone(single_prediction)

    def test_make_multiple_prediction(self):
        # When
        multiple_prediction = predict(input_data=self.test_data[0:10])

        # Then
        self.assertIsNotNone(multiple_prediction)


if __name__ == '__main__':
    unittest.main()
