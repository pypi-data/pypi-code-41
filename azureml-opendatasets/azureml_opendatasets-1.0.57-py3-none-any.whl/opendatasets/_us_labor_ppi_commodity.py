# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor ppi commodity."""

from ._abstract_opendataset import AbstractOpenDataset
from .accessories.us_labor_ppi_commodity_accessory import UsLaborPPICommodityAccessory
from azureml.core import Dataset


class UsLaborPPICommodity(AbstractOpenDataset):
    """US labor ppi commodity class."""

    def __init__(
            self,
            dataset: Dataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the UsLaborPPICommodity class.
        It can be initialized with or without dataset.

        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = UsLaborPPICommodityAccessory(enable_telemetry=enable_telemetry)
        if dataset is not None:
            worker.update_dataset(dataset, enable_telemetry=enable_telemetry)
            self.worker = worker
            Dataset.__init__(
                self,
                definition=dataset.get_definition(),
                workspace=dataset.workspace,
                name=dataset.name,
                id=dataset.id)
        else:
            AbstractOpenDataset.__init__(self, worker=worker)

    @staticmethod
    def get(dataset: Dataset, enable_telemetry: bool = True):
        """Get an instance of UsLaborPPICommodity.

        :param dataset: input an instance of Dataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of UsLaborPPICommodity.
        """
        pub = UsLaborPPICommodity(dataset=dataset, enable_telemetry=enable_telemetry)
        pub._tags = dataset.tags
        if enable_telemetry:
            AbstractOpenDataset.log_get_operation(pub.worker)
        return pub
