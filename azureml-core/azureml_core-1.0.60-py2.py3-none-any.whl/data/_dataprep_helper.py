# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for dataprep."""


def dataprep():
    import azureml.dataprep as _dprep
    return _dprep


def dataprep_fuse():
    import azureml.dataprep.fuse.dprepfuse as _dprep_fuse
    return _dprep_fuse


def ensure_dataflow(dataflow):
    if not isinstance(dataflow, dataprep().Dataflow):
        raise RuntimeError('dataflow must be instance of azureml.dataprep.Dataflow')
