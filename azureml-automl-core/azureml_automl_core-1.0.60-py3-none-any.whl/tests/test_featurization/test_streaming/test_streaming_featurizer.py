# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import tempfile
import unittest
from contextlib import contextmanager

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
from azureml.automl.core.featurization import StreamingFeaturizer


class StreamingFeaturizerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(StreamingFeaturizerTests, self).__init__(*args, **kwargs)
        self.simple_numbers_file = None
        self.simple_text_file = None

    def test_featurize_with_nans(self):
        train_df = self._get_xor_dataset()
        self.assertTrue(len(train_df[train_df['col1'].isnull()]) > 0)
        self.assertTrue(len(train_df[train_df['col2'].isnull()]) > 0)

        with dataframe_as_csv(train_df) as input_file:
            X_train = (dprep.read_csv(path=input_file).
                       drop_columns(columns=['label']).
                       to_number(columns=['col1', 'col2']))
            streaming_featurizer = StreamingFeaturizer()
            featurized_X = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
            self.assertTrue(len(featurized_X[featurized_X['col1'].isnull()]) == 0)
            self.assertTrue(len(featurized_X[featurized_X['col2'].isnull()]) == 0)

    def test_categoricals_with_two_categories(self):
        # Expecting categorical data with less than 1000 unique values to be one hot encoded
        train_set_category_array = np.repeat(['cat', 'bear'], 100)
        train_df = pd.DataFrame({'category': train_set_category_array})

        with dataframe_as_csv(train_df) as input_file:
            X_train = dprep.read_csv(path=input_file)
            streaming_featurizer = StreamingFeaturizer()
            _ = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()

            test = np.repeat(['cat', 'bear'], 2)
            test_df = pd.DataFrame({'category': test})
            test_transformed = streaming_featurizer.transform(test_df)

            expected_df = pd.DataFrame({'category.cat': [1.0, 1.0, 0.0, 0.0],
                                        'category.bear': [0.0, 0.0, 1.0, 1.0]})
            self.assertEqual(test_transformed['category.cat'].tolist(), expected_df['category.cat'].tolist())
            self.assertEqual(test_transformed['category.bear'].tolist(), expected_df['category.bear'].tolist())

    def test_drop_hashes(self):
        # Columns which are hashes should be dropped
        # todo Test should be updated once we have alternate column purpose detection, in which case the column
        #  should be converted to text and the transformations re-learnt
        n = 10000
        s1 = pd.Series(np.random.rand(n))
        train_df = pd.DataFrame(s1)
        train_df[0] = train_df[0].astype(str)

        with dataframe_as_csv(train_df) as input_file:
            X_train = dprep.read_csv(path=input_file)
            streaming_featurizer = StreamingFeaturizer()
            feat = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
            assert (feat.shape[0] == 0)

    def test_text_transform(self):
        train_df = pd.DataFrame(
            data=dict(
                review=[
                    "This is great",
                    "I hate it",
                    "Love it",
                    "Do not like it",
                    "Really like it",
                    "I hate it",
                    "I like it a lot",
                    "I kind of hate it",
                    "I do like it",
                    "I really hate it",
                    "It is very good",
                    "I hate it a bunch",
                    "I love it a bunch",
                    "I hate it",
                    "I like it very much",
                    "I hate it very much.",
                    "I really do love it",
                    "I really do hate it",
                    "Love it!",
                    "Hate it!",
                    "I love it",
                    "I hate it",
                    "I love it",
                    "I hate it",
                    "I love it"],
                like=[
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True]))

        test_reviews = pd.DataFrame(
            data=dict(
                review=[
                    "This is great",
                    "I hate it",
                    "Love it",
                    "Really like it",
                    "I hate it",
                    "I like it a lot",
                    "I love it",
                    "I do like it",
                    "I really hate it",
                    "I love it"]))

        with dataframe_as_csv(train_df) as input_file:
            X_train = dprep.read_csv(input_file).drop_columns(columns=['like'])
            streaming_featurizer = StreamingFeaturizer()

            featurized_X = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
            self.assertEqual(featurized_X.shape, (25, 83))

            test_transformed = streaming_featurizer.transform(test_reviews)
            self.assertEqual(test_transformed.shape, (10, 83))

    def test_multiple_text_transforms(self):
        # Each column should have it's own text transformer - they shouldn't be flattened
        series = [self._get_text_column(random_seed=i) for i in range(5)]
        train_df = pd.concat(series, axis=1)

        with dataframe_as_csv(train_df) as input_file:
            X_train = dprep.read_csv(input_file)
            streaming_featurizer = StreamingFeaturizer()

            featurized_X = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
            self.assertEqual(featurized_X.shape, (10, 249))
            self.assertTrue(len(streaming_featurizer._estimator._pipeline.steps) == 5,
                            "Expecting 5 separate NGram transformers for 5 input text columns")

    def test_flatten_similar_transforms(self):
        train_df = self._get_categorical_df(columns='ABC', rows=100, categories=2)

        with dataframe_as_csv(train_df) as input_file:
            X_train = dprep.read_csv(input_file)
            streaming_featurizer = StreamingFeaturizer()

            featurized_X = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
            self.assertEqual(featurized_X.shape, (100, 6))
            self.assertTrue(len(streaming_featurizer._estimator._pipeline.steps) == 1,
                            "Expecting just 1 transformer for the given input data")

    # todo: Uncomment once OneHotHash <-> Dprep issues are fixed
    # def test_flatten_similar_onehothash_transforms(self):
    #     # Columns can use different number of bits for the OneHotHash transforms
    #     # Test to check if all the transformers with same number of bits fall into the same bucket
    #     train_df = self._get_categorical_df(columns='ABC', rows=100, categories=50)
    #
    #     with dataframe_as_csv(train_df) as input_file:
    #         X_train = dprep.read_csv(input_file)
    #         streaming_featurizer = StreamingFeaturizer()
    #
    #         featurized_X = streaming_featurizer.featurize_dataflow(X_train).to_pandas_dataframe()
    #         self.assertEqual(featurized_X.shape, (100, 6))
    #         self.assertTrue(len(streaming_featurizer._estimator._pipeline.steps) == 1,
    #                         "Expecting just 1 transformer for the given input data")

    def _get_xor_dataset(self) -> pd.DataFrame:
        return pd.DataFrame({'col1': [0, 0, 1, 1, 0, 1, np.nan, 0, 1],
                             'col2': [0, 1, np.nan, 0, 1, 0, 0, 1, 0],
                             'label': [0, 1, 0, 1, 1, 1, 0, 1, 1]})

    def _get_text_column(self, rows=10, random_seed=37):
        # Return a pandas series of type Text
        import random
        word_list = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt " \
                    "ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco " \
                    " laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit " \
                    "in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat " \
                    "cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split(" ")

        random.seed(random_seed)
        sentence = []
        for i in range(rows):
            rand1 = random.randint(0, len(word_list) - 1)
            rand2 = random.randint(1, len(word_list) - 1)
            rand3 = random.randint(2, len(word_list) - 1)
            sentence.append(" ".join([word_list[rand1], word_list[rand2], word_list[rand3]]))

        return pd.Series(sentence)

    def _get_categorical_df(self, columns: str, rows: int, categories: int = 10) -> pd.DataFrame:
        # Return a pandas DataFrame made up of multiple categorical columns
        # Each char from 'columns' will combine with a 'rows' to produce a cell value
        # Make index = categories for a hash column
        data = {c: [str(c) + str(i % categories) for i in range(rows)]
                for c in columns}
        return pd.DataFrame(data, range(rows))


@contextmanager
def dataframe_as_csv(dataframe: pd.DataFrame):
    path = tempfile.NamedTemporaryFile(prefix='_test_streaming', suffix='.csv')
    path.close()
    dataframe.to_csv(path_or_buf=path.name, index=False)
    yield path.name
    os.remove(path.name)
