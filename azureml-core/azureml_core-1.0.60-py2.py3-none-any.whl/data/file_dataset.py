# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class that represents file dataset to use in Azure Machine Learning service."""

import os
from azureml.data._dataset import _Dataset
from azureml.data._dataprep_helper import dataprep, dataprep_fuse
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.data.constants import _PUBLIC_API
from azureml.data.dataset_error_handling import _try_execute


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class FileDataset(_Dataset):
    """The class that represents file dataset to use in Azure Machine Learning service.

    A FileDataset defines a series of lazily-evaluated, immutable operations to load data from the
    data source into file streams.

    Data is not loaded from the source until FileDataset is asked to deliver data.

    .. remarks::

        FileDataset is created using :func:`azureml.data.dataset_factory.FileDatasetFactory.from_files` from
        :class:`azureml.data.dataset_factory.FileDatasetFactory` class.

        FileDataset can be used as input of an experiment run. It can also be registered to workspace
        with a specified name and be retrieved by that name later.

        FileDataset can be subsetted by invoking different subsetting methods available on this class.
        The result of subsetting is always a new FileDataset.

        The actual data loading happens when FileDataset is asked to deliver the data into another
        storage mechanism (e.g. files downloaded or mounted to local path).
    """

    def __init__(self):
        """Initialize the FileDataset object.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.FileDatasetFactory` class.
        """
        super().__init__()

    @track(_get_logger, activity_type=_PUBLIC_API)
    def to_path(self):
        """Get a list of file paths for each file stream defined by the dataset.

        .. remarks::
            The file paths are relative paths for local files when the file streams are downloaded or mounted.

        :return: Returns an array of file paths.
        :rtype: numpy.ndarray
        """
        dataflow, portable_path = _add_portable_path_column(self._dataflow)
        return dataflow.to_pandas_dataframe()[portable_path].values

    @track(_get_logger, activity_type=_PUBLIC_API)
    def download(self, target_path, overwrite=False):
        """Download file streams defined by the dataset as local files.

        :param target_path: The local directory to download the files to.
        :type target_path: str
        :param overwrite: Whether to overwrite existing files. Defaults to False.
            Existing files will be overwritten if True, otherwise exception will be raised.
        :type overwrite: bool
        :return: Returns an array of file paths for each file downloaded.
        :rtype: numpy.ndarray
        """
        import numpy
        target_path = os.path.abspath(target_path)
        download_list = [os.path.abspath(os.path.join(target_path, '.' + p)) for p in self.to_path()]
        if not overwrite:
            for p in download_list:
                if os.path.exists(p):
                    raise RuntimeError('File "{}" already exists. Set overwrite=True to overwrite it.'
                                       .format(p))
        base_path = dataprep().api.datasources.LocalFileOutput(target_path)

        dataflow, portable_path = _add_portable_path_column(self._dataflow)
        dataflow = dataflow.write_streams(
            streams_column='Path',
            base_path=base_path,
            file_names_column=portable_path)
        _try_execute(dataflow.run_local)
        return numpy.asarray(download_list, 'O')

    @track(_get_logger, activity_type=_PUBLIC_API)
    def mount(self, mount_point):
        """Mount file streams defined by the dataset as local files.

        .. remarks::
            We will not unmount automatically, please run `sudo umount <mount_point>` to unmount.

        :param mount_point: The local directory to mount the files to.
        :type mount_point: str
        :return: Returns a context manager for managing the lifecycle of the mount.
        :rtype: azureml.dataprep.fuse.daemon.MountContext
        """
        try:
            mount = dataprep_fuse().mount
        except OSError:
            raise OSError('Mount is only supported on Unix or Unix-like operating systems.')

        mount_point = os.path.abspath(mount_point)
        if os.path.ismount(mount_point):
            raise RuntimeError('"{0}" is already mounted. Run `sudo umount "{0}"` to unmount it.'
                               .format(mount_point))
        return mount(
            dataflow=self._dataflow,
            files_column='Path',
            mount_point=mount_point,
            foreground=False)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def skip(self, count):
        """Skip file streams from top of the dataset by the specified count.

        :param count: The number of file streams to skip.
        :type count: int
        :return: Returns a new FileDataset object for the dataset with file streams skipped.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(self._dataflow.skip(count), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def take(self, count):
        """Take a sample of file streams from top of the dataset by the specified count.

        :param count: The number of file streams to take.
        :type count: int
        :return: Returns a new FileDataset object for the sampled dataset.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(self._dataflow.take(count), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def take_sample(self, probability, seed=None):
        """Take a random sample of file streams in the dataset approximately by the probability specified.

        :param probability: The probability of a file stream being included in the sample.
        :type probability: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a new FileDataset object for the sampled dataset.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(self._dataflow.take_sample(probability, seed), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def random_split(self, percentage, seed=None):
        """Split file streams in the dataset into two parts randomly and approximately by the percentage specified.

        :param percentage: The approximate percentage to split the Dataflow by. This must be a number between 0.0
            and 1.0.
        :type percentage: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a tuple of new FileDataset objects for the tow split datasets.
        :rtype: (azureml.data.FileDataset, azureml.data.FileDataset)
        """
        dataflow1, dataflow2 = self._dataflow.random_split(percentage, seed)
        return (
            FileDataset._create(dataflow1, self._properties),
            FileDataset._create(dataflow2, self._properties)
        )


def _add_portable_path_column(dataflow):
    portable_path = 'Portable Path'
    get_portable_path = dataprep().api.functions.get_portable_path
    col = dataprep().api.expressions.col
    return dataflow.add_column(get_portable_path(col('Path')), portable_path, 'Path'), portable_path
