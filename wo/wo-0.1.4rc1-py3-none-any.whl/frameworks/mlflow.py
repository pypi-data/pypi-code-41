import mlflow
import logging, sys, pprint

__all__ = ["MLflow"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MLflow:

    @staticmethod
    def set_endpoint(uri):
        """
        Set up tracking server, where MLflow instance is deployed. 

        Parameters
        ----------
        uri: str
            URI, where MLflow instance is deployed.
        """
        logger.info("Set MLflow tracking server to {}".format(uri))
        mlflow.set_tracking_uri(uri)

    @staticmethod
    def set_experiment(experiment):
        """
        Set experiment, where to log current/active run outcome. 

        Parameters
        ----------
        experiment: str
            Name of the experiment, where experiment will be tracked. 
        """
        logger.info("Set experiment to be `{}`".format(experiment))
        mlflow.set_experiment(experiment)
        
    @staticmethod
    def log_parameters(parameters, *args, **kwargs):
        """
        Log parameters, used in current/active run. 

        Parameters
        ----------
        parameters: dict
            Dictionary with parameters.
        """
        logger.info("Logging parameters to MLflow:\n{}".format(pprint.pformat(parameters)))
        mlflow.log_params(parameters)

    @staticmethod
    def log_metrics(metrics, step=None, *args, **kwargs):
        """
        Log metrics, produced in current/active run. 

        Parameters
        ----------
        metrics: dict
            Dictionary with metrics, recorded in current/active run. 
        step: int
            Step, at which given metrics were recorded. 
        """   
        logger.info("Logging metrics to MLflow:\n{}".format(pprint.pformat(metrics)))
        mlflow.log_metrics(metrics)
