# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class for input backed by streaming supported NimbusML transformers."""
import logging
from typing import List, Dict, Optional, Tuple

import pandas as pd
from azureml.automl.core.stats_computation import RawFeatureStats
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
        # Dictionary of <DataType> -> <List of columns>
        column_groups = {}  # type: Dict[str, List[Tuple[str, RawFeatureStats]]]
        for raw_stats, column_purpose, column in stats_and_column_purposes:
            column_groups.setdefault(column_purpose, []).append((column, raw_stats))

        column_groups_with_new_names = {purpose: self._map_to_new_column_names(columns_and_raw_stats)
                                        for purpose, columns_and_raw_stats in column_groups.items()}

        transforms = [self._get_transforms_for_column_purpose(k, v) for k, v in column_groups_with_new_names.items()]
        flattened_transforms = [transform for sublist in transforms for transform in sublist]

        # todo: sweep for alternate column purposes

        if not flattened_transforms:
            self._logger.warning("No features could be identified or generated. Please inspect your data.")
            raise ValueError("No features could be identified or generated. Please inspect your data.")

        return flattened_transforms

    def _map_to_new_column_names(self, column_list_with_stats: List[Tuple[str, RawFeatureStats]]) -> \
            Dict[str, Tuple[str, RawFeatureStats]]:
        column_list, raw_stats_list = [list(x) for x in zip(*column_list_with_stats)]
        raw_feature_names, new_column_names = data_transformer_utils.generate_new_column_names(column_list)
        return dict(zip(raw_feature_names, list(zip(new_column_names, raw_stats_list))))

    def _get_transforms_for_column_purpose(self,
                                           column_purpose: str,
                                           column_name_dict_with_stats: Dict[str, Tuple[str, RawFeatureStats]]) ->\
            List[BasePipelineItem]:
        # todo for all transforms, figure out right set of params
        result = []  # type: List[BasePipelineItem]
        column_dict = {raw_column_name: new_column_name
                       for raw_column_name, (new_column_name, _) in column_name_dict_with_stats.items()}
        if column_purpose == FeatureTypeRecognizer.Numeric:
            # todo add indicator column for missing values based on threshold
            # concat = False drops the indicator column
            result.append(Handler(columns=column_dict, replace_with='Mean', concat=False))
        elif column_purpose in [FeatureTypeRecognizer.Categorical, FeatureTypeRecognizer.CategoricalHash]:
            # todo see if we could use label_encoding (nimbus's ToKey transformer) for unique_vals <= 2
            # Using OneHotVectorizer for categorical hash as well, because of a bug mentioned below
            result.append(OneHotVectorizer(columns=column_dict))
        # todo: The following code is commented because there's a problem with using number_of_bits > 16
        # because of the way map_partition is implemented. Uncomment once the bug is fixed
        # elif column_purpose == FeatureTypeRecognizer.CategoricalHash:
        #     # Different columns may require different num_of_bits, in which case we might need to produce
        #     # multiple OneHotHash transformers. We try to optimize by flattening all the columns that have the same
        #     # number of bits
        #     onehothash_to_column = {}  # type: Dict[int, Dict[str, str]]
        #
        #     for raw_column_name, (new_column_name, raw_stats) in column_name_dict_with_stats.items():
        #         # todo What should be the appropriate value for number_of_bits?
        #         # NimusML only supports values ranging from 1-30, while our current AutoML logic
        #         # (commented out below) might produce values > 30. Until then, using a NimbusML default value of 16
        #         # number_of_bits = pow(2, int(math.log(raw_stats.num_unique_vals, 2)))
        #         number_of_bits = 6 # default value for NimbusML
        #         onehothash_to_column.setdefault(number_of_bits, {})[raw_column_name] = new_column_name
        #
        #     onehothash_transforms = []
        #     for number_of_bits, column_dict in onehothash_to_column.items():
        #         onehothash_transforms.append(OneHotHashVectorizer(columns=column_dict,
        #                                                           number_of_bits=number_of_bits))
        #
        #     result.extend(onehothash_transforms)
        elif column_purpose in [FeatureTypeRecognizer.Text, FeatureTypeRecognizer.DateTime]:
            ngram_transforms = []  # type: List[BasePipelineItem]
            for raw_column_name, (new_column_name, raw_stats) in column_name_dict_with_stats.items():
                ngram_length = int(get_ngram_len(raw_stats.lengths))
                ngram_transforms.append(NGramFeaturizer(columns={new_column_name: raw_column_name},
                                                        word_feature_extractor=Ngram(ngram_length=ngram_length),
                                                        char_feature_extractor=None))
            result.extend(ngram_transforms)
        elif column_purpose in FeatureTypeRecognizer.DROP_SET:
            raw_column_names_to_drop = list(column_dict.keys())
            result.append(ColumnSelector(columns=raw_column_names_to_drop, drop_columns=raw_column_names_to_drop))

        return result

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._estimator:
            raise ValueError('`transform()` called before learning the estimator.')

        return self._estimator.transform(df)
