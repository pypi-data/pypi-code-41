"""
Shared, static objects/exceptions/etc.
"""


class UnknownLabelingTask(Exception):
    """
    Labeling task with specified ID not found.
    """
    pass


class PurgedLabelingTask(Exception):
    """
    Results of labeling task with specified ID are no longer available. You'll need to resubmit this task.
    """


class FailedLabelingTask(Exception):
    """
    Labeling task failed to process. See webservice logs for more information.
    """


class ResultNotReady(Exception):
    """
    LabelingTask is still processing, result is not ready yet.
    """


class ConfigurationException(Exception):
    """
    Invalid or missing configuration; cannot use SDK without a valid configuration present.
    """
