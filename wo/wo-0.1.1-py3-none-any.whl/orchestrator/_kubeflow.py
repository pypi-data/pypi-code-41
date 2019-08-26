import os, json, logging, sys, pprint

__all__ = ["Kubeflow"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Kubeflow:

    @staticmethod
    def export_outputs(outputs, as_root=False):
        """
        Export outputs as files. 

        Parameters
        ----------
        outputs: dict
            Dictionary of outputs, which should be exported. Key will be interpreted as 
            file name, value will be interpreted as contents of the file. 
        as_root=False: bool
            If files should be saved on the root level. 
        """ 
        logger.info("Exporting outputs for Kubeflow:\n{}".format(pprint.pformat(outputs)))
        for key, value in outputs.items():
            if as_root and os.path.dirname(key) != "/":
                key = os.path.join("/", key)
            with open(key, "w+") as file:
                if key.endswith(".json"):
                    json.dump(value, file)
                else:
                    file.write(str(value))