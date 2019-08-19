# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class for input backed by streaming supported NimbusML transformers."""
import logging
from typing import List, Dict, Optional

import pandas as pd
from azureml.dataprep import Dataflow
from nimbusml.feature_extraction.categorical import OneHotHashVectorizer, OneHotVectorizer
from nimbusml.feature_extraction.text import NGramFeaturizer
from nimbusml.feature_extraction.text.extractor import Ngram
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem
from nimbusml.preprocessing.missing_values import Handler
from nimbusml.preprocessing.schema import ColumnSelector

from azureml.automl.core._engineered_feature_names import FeatureTypeRecognizer
from azureml.automl.core._experiment_observer import ExperimentStatus, ExperimentObserver, NullExperimentObserver
from azureml.automl.core.column_purpose_detection import ColumnPurposeDetector
from azureml.automl.core.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml.automl.core.featurization import data_transformer_utils
from azureml.automl.core.featurization.streaming.streaming_estimator import NimbusMLStreamingEstimator, \
    StreamingEstimatorBase
from azureml.automl.core.featurization.streaming.streaming_pipeline_executor import StreamingPipelineExecutor


# TODO: ONNX, Explainability
from azureml.automl.core.featurizer.transformer import get_ngram_len


class StreamingFeaturizer:
    MAX_ROWS_TO_SUBSAMPLE = 100000

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 observer: Optional[ExperimentObserver] = None):
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._observer = observer or NullExperimentObserver()
        self._estimator = None  # type: Optional[StreamingEstimatorBase]

    def featurize_dataflow(self, df: Dataflow, y: Optional[Dataflow] = None) -> Dataflow:
        # todo y is currently unused, might need it for feature sweeping?
        if not isinstance(df, Dataflow):
            raise ValueError('NimbusML data transformer requires AzureML DataFlow as input. Received type: {}'.
                             format(df.__class__.__name__))

        # todo replace with the one from training utilities
        subsampled_input = df.head(StreamingFeaturizer.MAX_ROWS_TO_SUBSAMPLE)

        self._observer.report_status(
            ExperimentStatus.DatasetEvaluation, "Gathering dataset statistics.")

        stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(subsampled_input)

        self._observer.report_status(
            ExperimentStatus.FeaturesGeneration, "Generating features for the dataset.")

        transformations = self._get_transformations(stats_and_column_purposes)
        # todo this should be generalized, we will be getting non-nimbus estimators as well in the near future
        self._estimator = NimbusMLStreamingEstimator(transformations)
        return StreamingPipelineExecutor.execute_pipeline([self._estimator], df)

    def _get_transformations(self,
                             stats_and_column_purposes: List[StatsAndColumnPurposeType]) -> List[BasePipelineItem]:
        steps = []  # type: List[BasePipelineItem]

        # Dictionary of <DataType> -> <List of columns>
        column_groups = {}  # type: Dict[str, List[str]]
        for _, column_purpose, column in stats_and_column_purposes:
            column_groups.setdefault(column_purpose, []).append(column)

        # for each of the unique datatypes found in the input, we will featurize the corresponding columns
        for column_purpose, column_list in column_groups.items():
            transforms = self._get_transforms_for_column_purpose(stats_and_column_purposes,
                                                                 column_purpose, column_list)
            steps.extend(transforms)

        # todo: sweep for alternate column purposes

        if not steps:
            self._logger.warning("No features could be identified or generated. Please inspect your data.")
            raise ValueError("No features could be identified or generated. Please inspect your data.")

        return steps

    def _get_transforms_for_column_purpose(self,
                                           stats_and_column_purposes: List[StatsAndColumnPurposeType],
                                           column_purpose: str,
                                           column_list: List[str]) -> List[BasePipelineItem]:
        # todo for all transforms, figure out right set of params
        # todo for all transforms, replace column_list with dictionary of old_name -> new_name

        result = []  # type: List[BasePipelineItem]

        # todo optimize it so that this doesn't happen for each column
        raw_feature_names, new_column_names = data_transformer_utils.generate_new_column_names(column_list)
        column_dict = dict(zip(raw_feature_names, new_column_names))
        for column in column_list:
            # get the raw stats for the current column
            stats_and_column_purpose = next(x for x in stats_and_column_purposes if x[2] == column)
            index = stats_and_column_purposes.index(stats_and_column_purpose)
            raw_stats, _, _ = stats_and_column_purposes[index]

            if column_purpose == FeatureTypeRecognizer.Numeric:
                # todo add indicator column for missing values based on threshold
                missing_values_imputer = Handler(columns={column: column_dict[column]},
                                                 replace_with='Mean',
                                                 concat=False)
                result.extend([missing_values_imputer])

            if column_purpose in [FeatureTypeRecognizer.Categorical, FeatureTypeRecognizer.CategoricalHash]:
                # todo see if we could use label_encoding (nimbus's ToKey transformer) for unique_vals <= 2
                if raw_stats.num_unique_vals <= 1000:
                    onehot_transform = OneHotVectorizer(columns=[column])
                    result.append(onehot_transform)
                else:
                    onehothash_transform = OneHotHashVectorizer(columns=[column])
                    result.append(onehothash_transform)

            if column_purpose == FeatureTypeRecognizer.Text:
                text_transform = NGramFeaturizer(columns=[column],
                                                 word_feature_extractor=Ngram(
                                                     ngram_length=int(get_ngram_len(raw_stats.lengths))),
                                                 char_feature_extractor=None)
                result.append(text_transform)

            if column_purpose == FeatureTypeRecognizer.DateTime:
                pass

            if column_purpose in FeatureTypeRecognizer.DROP_SET:
                transform = ColumnSelector(columns=[column], drop_columns=[column])
                result.append(transform)

        if not result:
            self._logger.info("Hashes or single value column detected. No transforms needed")

        return result

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._estimator:
            raise ValueError('`transform()` called before learning the estimator.')

        return self._estimator.transform(df)
