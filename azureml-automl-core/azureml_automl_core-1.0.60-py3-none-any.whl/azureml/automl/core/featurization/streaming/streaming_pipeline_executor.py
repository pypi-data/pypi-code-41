# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pickle
from typing import List

from azureml.dataprep import Dataflow

from azureml.automl.core.featurization.streaming.streaming_estimator import StreamingEstimatorBase


class StreamingPipelineExecutor:
    _TRANSFORM_PARTITION_SCRIPT = """def transform(df, index):
    import pickle
    import nimbusml
    pipeline_bytes = {}
    pipeline = pickle.loads(pipeline_bytes)
    return pipeline.transform(df)"""

    @staticmethod
    def execute_pipeline(estimators: List[StreamingEstimatorBase], dataflow: Dataflow) -> Dataflow:
        # todo should group by different estimators later on
        assert len(estimators) == 1, "Expecting only NimbusML estimators for now"
        estimators[0].fit(dataflow)
        # todo: use map_partition from new dprep
        return dataflow.transform_partition(StreamingPipelineExecutor._TRANSFORM_PARTITION_SCRIPT.format
                                            (pickle.dumps(estimators[0])))
