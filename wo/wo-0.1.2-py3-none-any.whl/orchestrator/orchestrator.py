from wo.utils.config import DefaultParamDict
from wo.frameworks._mlflow import MLflow
from wo.orchestrator._kubernetes import Kubernetes
from wo.orchestrator._kubeflow import Kubeflow
from wo.orchestrator.storage import Storage
import datetime, logging, sys, os

__all__ = ["Orchestrator"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Orchestrator(Storage, MLflow):
    
    def __init__(self, experiment=None, default_params=None, default_logs_path="logs/", 
        use_mlflow=False, is_dev=False, is_kubeflow=True):
        """
        Initialize orchestrator instance. 

        Parameters
        ----------
        experiment=None: str
            Experiment name, which will be used to track current execution.
        default_params=None: dict
            Default parameters, required for this execution. 
        default_logs_path="logs/": str
            Default path, where logs of the current run will be stored.
        use_mlflow=False: bool
            Flag, indicating whether to use MLflow in current run.
        is_dev=False: bool
            Flag, indicating whether this is a dry run. 
        is_kubeflow=True: bool 
            Flag, indicating whether this execution is orchestrated by Kubeflow. 
        """
        self.experiment = experiment or "Default"
        self.default_params = DefaultParamDict(
            dict() if not default_params else default_params)
        self.default_logs_path = default_logs_path
        self.logger = logging.getLogger(__name__)
        self.__mlflow = use_mlflow
        self.__kubeflow = is_kubeflow
        self.__dev = is_dev

        if self.__mlflow:
            MLflow.set_endpoint(self.get_config()["uri.mlflow"])
            MLflow.set_experiment(self.experiment)
        if self.__dev:
            self.logger.setLevel(logging.DEBUG)        

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
        logs_file=None: str
            File, where logs of the current execution were written. 
        logs_bucket=None: str
            Bucket, where logs should be uploaded. 
        logs_path=None: str
            Path, under which logs of the current execution should be uploaded. 
        """
        logger.info("Logging current execution")

        if logs_file and not self.__dev:
            # Do not upload logs in `dev` execution
            if not logs_bucket: 
                raise ValueError("`logs_bucket` must be provided along with `logs_file`")

            timestamp = datetime.datetime.utcnow().isoformat("T") + ".log"
            logs_file = ".".join(logs_file.split(".")[:-1])
            logs_path = logs_path or self.default_logs_path
            logs_path = os.path.join(
                logs_bucket, logs_path, logs_file, timestamp)
            
            if outputs: outputs["logs_path"] = logs_path
            else: outputs = {"logs_path": logs_path}
            self.upload_file(logs_file, logs_path)
        
        if outputs and self.__kubeflow:
            Kubeflow.export_outputs(outputs, as_root=not self.__dev)
        if metrics and self.__mlflow:
            MLflow.log_metrics(metrics)
        if parameters and self.__mlflow:
            MLflow.log_parameters(parameters)