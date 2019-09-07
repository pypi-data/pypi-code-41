import os, logging, sys
from wo.utils.config import DefaultParamDict

__all__ = ["Kubernetes"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Kubernetes:
    
    @staticmethod
    def _get_config_map(default_dict, mount_path="/etc/config", **kwargs):
        """ 
        Parse mounted ConfigMap into Python dictionary.   

        Parameters
        ----------
        default_dict: DefaultParamDict
            Dictionary with default values.
        mount_path: str
            Path, where ConfigMap was mounted. 
        
        Returns
        -------
        dict
            A dictionary with a key corresponding to a filename and a value 
            corresponding to the file contents. 
        """
        logger.debug("Parsing configuration from `{}`".format(mount_path))
        for root, _, files in os.walk(mount_path):
            for file in files:
                key = os.path.join(os.path.relpath(root, mount_path), file)
                with open(os.path.join(root, file), "r") as value: 
                    default_dict[os.path.basename(key)] = value.read()
        return dict(default_dict)