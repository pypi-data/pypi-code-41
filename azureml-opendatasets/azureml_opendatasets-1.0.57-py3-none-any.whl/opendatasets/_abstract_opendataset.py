# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AbstractOpenDataset is the abstract base class of all OpenDataset."""

from .accessories.public_data import PublicData
from azureml.core import Dataset
from ._utils.telemetry_utils import get_opendatasets_logger
from azureml.telemetry.activity import ActivityType, log_activity
from typing import Optional
import azureml.dataprep as dprep
import uuid


class AbstractOpenDataset(Dataset):
    """AbstractOpenDataset is the abstract base class of all OpenDataset."""
    def __init__(
            self,
            worker: PublicData,
            partition_prep_func: Optional[object] = None):
        """
        Initialize AbstractOpenDataset with blob url.

        :param worker: an instance of PublicData.
        :type worker: PublicData
        :param partition_prep_func: a function to support partition path.
        :type partition_prep_func: object
        """
        self.worker = worker
        dflow = dprep.Dataflow.get_files(path=worker._blobInfo.get_url())

        if (partition_prep_func is not None):
            dflow_filtered = partition_prep_func(dflow, worker.start_date, worker.end_date)
        else:
            dflow_filtered = dflow

        # Read Blob files.
        dflow_read = dflow_filtered.read_parquet_file()

        # Use dataprep to filter dataset and return the filtered dataset object.
        if (bool(worker.time_column_name)):
            updated_dflow = dflow_read.filter(
                dprep.f_and(
                    dflow_read[worker.time_column_name] >= worker.start_date,
                    dflow_read[worker.time_column_name] <= worker.end_date))
        else:
            updated_dflow = dflow_read

        if len(worker.selected_columns) != 1 or worker.selected_columns[0] != '*':
            updated_dflow = updated_dflow.keep_columns(worker.selected_columns)
        new_ds = Dataset._from_dataflow(updated_dflow)
        Dataset.__init__(self, definition=new_ds.get_definition())

    @staticmethod
    def log_get_operation(public_data: PublicData):
        logger = get_opendatasets_logger(__name__)
        custom_dimensions = public_data.log_properties or {}
        custom_dimensions['activity_id'] = str(uuid.uuid4())
        custom_dimensions['activity_name'] = 'opendataset.get'
        custom_dimensions['activity_type'] = ActivityType.PUBLICAPI
        logger.info('Initialized from Dataset.', extra=custom_dimensions)

    def register(self, workspace, name, description=None, tags=None,
                 visible=True, exist_ok=False, update_if_exist=False):
        """Register the Dataset in the workspace, making it available to other users of the workspace.

        :param workspace: The AzureML workspace in which the Dataset is to be registered
        :type workspace: azureml.core.Workspace
        :param name: The name of the Dataset in the workspace
        :type name: str
        :param description: Description of the Dataset.
        :type description: str, optional
        :param tags: Tags to associate with the Dataset.
        :type tags: dict[str,str], optional
        :param visible: Controls visibility of the Dataset to the user in the UI.
            false=hidden in UI, available via SDK.
        :type visible: bool, optional
        :param exist_ok: If True the method returns the Dataset if it already exists in the given workspace, else error
        :type exist_ok: bool, optional
        :param update_if_exist: If exist_ok is True and update_if_exist is True, this method will update
            the definition and return the updated Dataset.
        :type update_if_exist: bool, optional
        :return: Registered Dataset object in the workspace.
        :rtype: azureml.core.dataset.Dataset
        """
        if self.worker.enable_telemetry:
            with log_activity(
                    self.worker.logger,
                    'register',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.worker.log_properties):
                tags = tags or {}
                tags['opendatasets'] = self.worker.registry_id
                return super(AbstractOpenDataset, self).register(
                    workspace, name, description=description, tags=tags, visible=visible, exist_ok=exist_ok,
                    update_if_exist=update_if_exist)
        else:
            return super(AbstractOpenDataset, self).register(
                workspace, name, description=description, tags=tags, visible=visible, exist_ok=exist_ok,
                update_if_exist=update_if_exist)

    def to_pandas_dataframe(self):
        """Create a Pandas dataframe by executing the transformation pipeline defined by this Dataset definition.

        .. remarks::

            Return a Pandas DataFrame fully materialized in memory.

        :return: A Pandas DataFrame.
        :rtype: pandas.core.frame.DataFrame
        """
        if self.worker.enable_telemetry:
            with log_activity(
                    self.worker.logger,
                    'to_pandas_dataframe',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.worker.log_properties):
                if self.worker.dataset is None:
                    return self.worker.to_pandas_dataframe()
                return super(AbstractOpenDataset, self).to_pandas_dataframe()
        else:
            if self.worker.dataset is None:
                return self.worker.to_pandas_dataframe()
            return super(AbstractOpenDataset, self).to_pandas_dataframe()

    def to_spark_dataframe(self):
        """Create a Spark DataFrame that can execute the transformation pipeline defined by this Dataset definition.

        .. remarks::

            The Spark Dataframe returned is only an execution plan and does not actually contain any data,
            as Spark Dataframes are lazily evaluated.

        :return: A Spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        if self.worker.enable_telemetry:
            with log_activity(
                    self.worker.logger,
                    'to_spark_dataframe',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.worker.log_properties):
                if self.worker.dataset is None:
                    return self.worker.to_spark_dataframe()
                return super(AbstractOpenDataset, self).to_spark_dataframe()
        else:
            if self.worker.dataset is None:
                return self.worker.to_spark_dataframe()
            return super(AbstractOpenDataset, self).to_spark_dataframe()

    def generate_profile(self, compute_target=None, workspace=None, arguments=None):
        """Generate new profile for the Dataset.

        .. remarks::

             Synchronous call, will block till it completes. Call :func: get_result to get the result of
                the action.

        :param compute_target: compute target to perform the snapshot profile creation, optional.
            If omitted, the local compute is used.
        :type compute_target: azureml.core.compute.ComputeTarget or str, optional
        :param workspace: Workspace, required for transient(unregistered) Datasets.
        :type workspace: azureml.core.Workspace, optional
        :param arguments: Profile arguments. Valid arguments are

            +--------------------------+--------------------+--------------------------------------+
            |         Argument         |        Type        |              Description             |
            +--------------------------+--------------------+--------------------------------------+
            |   include_stype_counts   |        bool        | Check if values look like some       |
            |                          |                    | well known semantic types            |
            |                          |                    | - email address, IP Address (V4/V6), |
            |                          |                    | US phone number, US zipcode,         |
            |                          |                    | Latitude/Longitude                   |
            |                          |                    | Turning this on impacts performance. |
            +--------------------------+--------------------+--------------------------------------+
            | number_of_histogram_bins |        int         | Number of histogram bins to use for  |
            |                          |                    | numeric data, default value is 10    |
            +--------------------------+--------------------+--------------------------------------+

        :type arguments: Dict[str,object], optional
        :return: Dataset action run object.
        :rtype: azureml.data.dataset_action_run.DatasetActionRun
        """
        if self.worker.enable_telemetry:
            with log_activity(
                    self.worker.logger,
                    'generate_profile',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.worker.log_properties):
                return super(AbstractOpenDataset, self).generate_profile(
                    compute_target=compute_target,
                    workspace=workspace,
                    arguments=arguments)
        else:
            return super(AbstractOpenDataset, self).generate_profile(
                compute_target=compute_target,
                workspace=workspace,
                arguments=arguments)

    def get_profile(self, arguments=None, generate_if_not_exist=True, workspace=None, compute_target=None):
        """Get summary statistics on the Dataset computed earlier.

        .. remarks::

            For a Dataset registered with an AML workspace, this method retrieves an existing profile that
                was created earlier by calling :func: get_profile if it is still valid. Profiles are invalidated
                when changed data is detected in the Dataset or the arguments to get_profile are different from
                the ones used when the profile was generated. If the profile is not present or invalidated,
                generate_if_not_exist will determine if a new profile is generated.

            For a Dataset that is not registered with an AML workspace, this method always runs generate_profile
                and returns the result.

        :param arguments: Profile arguments.
        :type arguments: Dict[str,object], optional
        :param generate_if_not_exist: generate profile if it does not exist.
        :type generate_if_not_exist: bool, optional
        :param workspace: Workspace, required for transient(unregistered) Datasets.
        :type workspace: azureml.core.Workspace, optional
        :param compute_target: compute target to execute the profile action, optional.
        :type compute_target: azureml.core.compute.ComputeTarget or str, optional
        :return: DataProfile of the Dataset.
        :rtype: azureml.dataprep.DataProfile
        """
        if self.worker.enable_telemetry:
            with log_activity(
                    self.worker.logger,
                    'generate_profile',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.worker.log_properties):
                return super(AbstractOpenDataset, self).get_profile(
                    arguments=arguments,
                    generate_if_not_exist=generate_if_not_exist,
                    workspace=workspace,
                    compute_target=compute_target)
        else:
            return super(AbstractOpenDataset, self).get_profile(
                arguments=arguments,
                generate_if_not_exist=generate_if_not_exist,
                workspace=workspace,
                compute_target=compute_target)
