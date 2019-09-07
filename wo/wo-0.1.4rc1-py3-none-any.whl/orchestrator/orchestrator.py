import logging, sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from typing import List
from wo.utils.config import DefaultParamDict
from wo.frameworks.mlflow import MLflow
from wo.orchestrator.kubernetes import Kubernetes
from wo.orchestrator.kubeflow import Kubeflow
from wo.orchestrator.storage import Storage
import datetime, os

__all__ = ["Orchestrator"]


class Orchestrator2:

    def download_artifacts(self, *args, **kwargs):
        pass 

    def main(self, *args, **kwargs):
        pass 

    def upload_artifacts(self, *args, **kwargs):
        pass


class Orchestrator(Storage, MLflow):
    
    def __init__(self, inputs=None, outputs=None, logs_file=None, logs_bucket=None, 
        experiment="Default", default_params=None, mlflow=False, dev=False, kubeflow=True
    ):
        """
        Initialize orchestrator instance. 

        Parameters
        ----------
        inputs: List[tuple]
            Inputs of the step, that should be downloaded locally. Presented as a list 
            of 2-element tuples, where the first element is a source location of the data 
            and the second element is the local destination of the data.  

            ```
            with wo.Orchestrator(inputs=[("s3://bucket/data", "data"), ("s3://bucket/model", "model")]) as w:
                assert os.path.exists("data")
                assert ps.path.exists("model")
            ```

        outputs: List[tuple]
            Outputs of the step, that should be uploaded to the cloud after execution completes.
            Presented as a list of 2-element tuples, where the first element is a source location 
            of the data and the second element is the local destination of the data. 

            ```
            with wo.Orchestrator(outputs=[("transformer/", "s3://bucket/transformer/")]) as w:
                # execute code 
            ```

        logs_file=None: str
            File, where logs of the current execution were written. 
        logs_bucket=None: str
            Bucket, where logs should be uploaded. 

        default_params: dict
            Default parameters, required for this execution. 

        experiment="Default": str
            Experiment name, which will be used to track current execution.
        
        mlflow=False: bool
            Flag, indicating whether to use MLflow in current run.
        kubeflow=True: bool 
            Flag, indicating whether this execution is orchestrated by Kubeflow. 
        dev=False: bool
            Flag, indicating whether this is a dry run. 
        """
        self.inputs = inputs or []
        self.outputs = outputs or []

        self.logs_file = logs_file
        self.logs_bucket = logs_bucket

        self.default_params = DefaultParamDict(
            {} if not default_params else default_params)

        self.experiment = experiment
        self.__kubeflow, self.__mlflow, self.__dev = kubeflow, mlflow, dev

        if self.__mlflow:
            MLflow.set_endpoint(self.get_config()["uri.mlflow"])
            MLflow.set_experiment(self.experiment)
        if self.__dev:
            logger.setLevel(logging.DEBUG)     

    def __enter__(self):
        for source, destination in self.inputs:
            if self.object_exists(source): 
                self.download_file(source, destination)
            else: 
                self.download_prefix(source, destination)
        return self

    def __exit__(self, *args):
        try: 
            if (self.logs_file or self.logs_bucket) and not self.__dev:
                assert self.logs_file, "`logs_file` must be provided along with `logs_bucket`"
                assert self.logs_bucket, "`logs_bucket` must be provided along with `logs_file`"

                timestamp = datetime.datetime.utcnow().isoformat("T") + ".log"
                logs_prefix = ".".join(self.logs_file.split(".")[:-1])
                logs_path = os.path.join(self.logs_bucket, logs_prefix, timestamp)

                self.upload_file(self.logs_file, logs_path)
                self.log_execution(outputs={"logs_path": logs_path})
                
            for source, destination in self.outputs:
                if os.path.isfile(source):
                    self.upload_prefix(source, destination)
                else: 
                    self.upload_prefix(source, destination)
        except: 
            return False
        

    def get_config(self, **kwargs):
        """
        Get configuration for current execution.

        Returns
        -------
        dict: 
            Dictionary, containing configuration for the current execution. 
        """
        return Kubernetes._get_config_map(self.default_params, **kwargs)

    def log_execution(self, outputs=None, parameters=None, metrics=None, 
        logs_file=None, logs_bucket=None, logs_path=None, *args, **kwargs):
        """
        Log all produced information to the underlying infrastructure. 

        Parameters
        ----------
        outputs=None: dict
            Outputs of the current execution. The following steps of the workflow may
            rely on this data. This might be cloud path to the artifacts, etc. 
        parameters=None: dict
            Parameters, used in the current execution to configure computation path. 
        metrics=None: dict
            Metrics, generated in the current execution. 
        """
        if outputs and self.__kubeflow:
            Kubeflow.export_outputs(outputs, as_root=not self.__dev)
        if metrics and self.__mlflow:
            MLflow.log_metrics(metrics)
        if parameters and self.__mlflow:
            MLflow.log_parameters(parameters)


if __name__ == "__main__":
    inputs=[("s3://workshop-hydrosphere/data/splitted/sample_version=1fad58e201a439470901b583212d9bb8", "data")]
    outputs=[("data", "s3://workshop-hydrosphere/data/splitt")]
    with Orchestrator(outputs=outputs) as w:
        pass