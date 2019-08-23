# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for dataset error handling in Azure Machine Learning service."""

from azureml.data._dataprep_helper import dataprep, ensure_dataflow


class DatasetValidationError(Exception):
    """Exception class for datasets validation error."""

    def __init__(self, message):
        """Class DatasetValidationError constructor.

        :param message: The error message.
        :type message: str
        """
        super().__init__(message)


class DatasetExecutionError(Exception):
    """Exception class for datasets execution error."""

    def __init__(self, message):
        """Class DatasetExecutionError constructor.

        :param message: The error message.
        :type message: str
        """
        super().__init__(message)


def _validate_has_data(dataflow, error_message):
    ensure_dataflow(dataflow)
    try:
        dataflow.verify_has_data()
    except (dataprep().api.dataflow.DataflowValidationError,
            dataprep().api.errorhandlers.ExecutionError):
        raise DatasetValidationError(error_message)
    except Exception as e:
        raise e


def _try_execute(action):
    try:
        return action()
    except Exception as e:
        raise DatasetExecutionError(str(e))
