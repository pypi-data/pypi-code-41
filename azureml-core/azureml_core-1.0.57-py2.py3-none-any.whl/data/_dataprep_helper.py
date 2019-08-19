# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for dataprep."""


def dataprep():
    import azureml.dataprep as _dprep
    return _dprep


def ensure_dataflow(dataflow):
    if not isinstance(dataflow, dataprep().Dataflow):
        raise RuntimeError('dataflow must be instance of azureml.dataprep.Dataflow')
