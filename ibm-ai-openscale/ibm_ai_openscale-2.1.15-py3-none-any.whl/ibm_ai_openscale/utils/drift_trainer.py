# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import logging
from ibm_ai_openscale.utils import install_package


class DriftTrainer():
    """
        Wrapper Class to generate information needed for error model, constraints
        :param training_data_frame: Dataframe comprising of input training data
        :type training_data_frame: DataFrame

        :param drift_detection_input: Input parameters needed for error model creation
        :type drift_detection_input:dict

        Example:
        drift_detection_input = {
            "feature_columns":<list of feature columns>
            "categorical_columns": <list of categorical columns>
            "label_column": <label column>
            "problem_type": <problem_type>
        }

    """

    def __init__(self, training_dataframe, drift_detection_input):
        initial_level = logging.getLogger().getEffectiveLevel()
        updated_level = logging.getLogger().getEffectiveLevel()

        if initial_level != updated_level:
            logging.basicConfig(level=initial_level)

        install_package("ibm-wos-utils")

        from ibm_wos_utils.drift.drift_trainer import DriftTrainer as DT
        self.__drift_trainer = DT(training_dataframe, drift_detection_input)
        self.drift_detection_model = None
        self.constraints = None

    def generate_drift_detection_model(self, score, optimise=True,
                                       callback=None, progress_bar=True, batch_size=5000):
        """Generates the drift detection model.

        Arguments:
            score {function} -- A function that accepts a dataframe with features as columns and returns a tuple of numpy array
                of probabilities array of shape `(n_samples,n_classes)` and numpy array of prediction vector of shape `(n_samples,)`

        Keyword Arguments:
            optimise {bool} -- If True, does hyperparameter optimisation for the drift detection model (default: {True})
            callback {function} -- A method to call after every iteration. (default: {None})
            progress_bar {bool} -- If True, shows progress bars. (default: {True})
            batch_size {int} -- Number of rows to score at a time. (default: {5000})
        """
        self.__drift_trainer.generate_drift_detection_model(
            score, batch_size=batch_size)
        self.drift_detection_model = self.__drift_trainer.drift_detection_model

    def learn_constraints(self):
        """Learn the constraints from training data."""
        self.__drift_trainer.learn_constraints()
        self.constraints = self.__drift_trainer.constraints

    @staticmethod
    def create_model_tar(drift_detection_model, constraints=None, path_prefix=".",
                         file_name="drift_detection_model.tar.gz"):
        """Creates a tar file for the drift detection model

        Arguments:
            drift_detection_model {DriftDetectionModel} -- the drift detection model to save

        Keyword Arguments:
            path_prefix {str} -- path of the directory to save the file (default: {"."})
            file_name {str} -- name of the tar file (default: {"drift_detection_model.tar.gz"})

        Raises:
            Exception: If there is an issue while creating directory, pickling the model or creating the tar file
        """
        from ibm_wos_utils.drift.drift_trainer import DriftTrainer as DT
        DT.create_model_tar(drift_detection_model=drift_detection_model,
                            constraints=constraints, path_prefix=path_prefix, file_name=file_name)
