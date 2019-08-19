# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class for input backed by streaming supported transformers."""
from abc import ABC, abstractmethod
from typing import List, Any

from azureml.dataprep import Dataflow
from nimbusml import Pipeline
from nimbusml import DprepDataStream
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem
from pandas import DataFrame


class StreamingEstimatorBase(ABC):
    """
    Base class for all estimators that can adhere to the streaming paradigm

    All sub-classes are required to override:
    1. A fit() method, that can accept and understand an AzureML Dataflow object.
    2. A transform() method that reads in a pandas.DataFrame object and produces a transformed pandas.DataFrame object

    The underlying framework should handle the batched transformation of StreamingInputType, depending on the memory
    pressures.
    """

    @abstractmethod
    def fit(self, dataflow: Dataflow) -> Any:
        raise NotImplementedError

    @abstractmethod
    def transform(self, dataframe: DataFrame) -> DataFrame:
        raise NotImplementedError


class NimbusMLStreamingEstimator(StreamingEstimatorBase):
    """
    Estimator class for NimbusML based estimators.
    """

    def __init__(self, steps: List[BasePipelineItem]):
        self._pipeline = Pipeline(steps=steps)

    def fit(self, dataflow: Dataflow) -> Any:
        # todo: X and y are combined in a single dataflow?
        datastream = DprepDataStream(dataflow)
        self._pipeline.fit(datastream)

    def transform(self, dataframe: DataFrame) -> DataFrame:
        return self._pipeline.transform(dataframe)
