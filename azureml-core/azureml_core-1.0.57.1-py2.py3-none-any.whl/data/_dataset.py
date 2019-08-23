# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Abstract Dataset class."""

from abc import ABCMeta
import re
import json

from msrest.exceptions import HttpOperationError
from azureml._base_sdk_common import _ClientSessionId
from azureml.data.dataset_factory import TabularDatasetFactory
from azureml.data._dataprep_helper import dataprep
from azureml.data._dataset_rest_helper import _dto_to_dataset, _dataset_to_dto, _restclient
from azureml.data._loggerfactory import track, _LoggerFactory


_PUBLIC_API = 'PublicApi'
_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class _Dataset(object):
    """Base class of datasets in Azure Machine Learning service."""

    __metaclass__ = ABCMeta

    Tabular = TabularDatasetFactory

    def __init__(self):
        """Class _Dataset constructor.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class
        """
        if self.__class__ == _Dataset:
            raise RuntimeError('Cannot create instance of absctract class _Dataset')
        self._definition = None
        self._registration = None

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_by_name(workspace, name, version='latest'):
        """Gets a Dataset from workspace by its registration name.

        :param workspace: The existing AzureML workspace in which the Dataset was created.
        :type workspace: azureml.core.Workspace
        :param name: The registration name.
        :type name: str
        :param version: The registration version. Defaults to 'latest'.
        :type version: int
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset
        """
        is_latest = version == 'latest'
        if not is_latest:
            try:
                version = int(version)
            except ValueError:
                raise ValueError('Invalid value {} for version. Version value must be number or "latest".'
                                 .format(version))
        try:
            dto = _restclient(workspace).dataset.get_dataset_by_name(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_name=name,
                include_latest_definition=is_latest,
                custom_headers=_custom_headers)
            if not is_latest:
                definition_dto = _restclient(workspace).dataset.get_dataset_definition(
                    workspace.subscription_id,
                    workspace.resource_group,
                    workspace.name,
                    dataset_id=dto.dataset_id,
                    version=str(version),
                    custom_headers=_custom_headers)
                dto.latest = definition_dto
            return _dto_to_dataset(workspace, dto)
        except HttpOperationError as e:
            if e.response.status_code == 404:
                raise Exception('Dataset with name "{0}" is not registered in the workspace'.format(name))
            else:
                raise e  # TODO: log unknown exception

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def id(self):
        """Returns the registration id.

        :return: Dataset id.
        :rtype: str
        """
        return None if self._registration is None else self._registration.id

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def name(self):
        """Returns the registration name.

        :return: Dataset name.
        :rtype: str
        """
        return None if self._registration is None else self._registration.name

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def version(self):
        """Returns the registration version.

        :return: Dataset version.
        :rtype: str
        """
        return None if self._registration is None else self._registration.version

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def description(self):
        """Returns the registration description.

        :return: Dataset description.
        :rtype: str
        """
        return None if self._registration is None else self._registration.description

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def tags(self):
        """Returns the registration tags.

        :return: Dataset tags.
        :rtype: str
        """
        return None if self._registration is None else self._registration.tags

    @property
    @track(_get_logger)
    def _dataflow(self):
        if self._definition is None:
            raise RuntimeError('Dataset definition is missing. Please check how the dataset is created.')
        if not isinstance(self._definition, dataprep().Dataflow):
            self._definition = dataprep().Dataflow.from_json(self._definition)
        return self._definition

    @track(_get_logger, activity_type=_PUBLIC_API)
    def register(self, workspace, name, description=None, tags=None, create_new_version=False):
        """Registers the dataset to the provided workspace.

        :param workspace: The workspace to register the dataset.
        :type workspace: azureml.core.Workspace
        :param name: The name to register the dataset with.
        :type name: str
        :param description: A text description of the dataset. Defaults to None.
        :type description: str
        :param tags: Dictionary of key value tags to give the dataset. Defaults to None.
        :type tags: dict[str, str]
        :param create_new_version: Boolean to register the dataset as a new version under the specified name.
        :type create_new_version: bool
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset
        """
        new_dto = _dataset_to_dto(self, name, description, tags)
        if create_new_version:
            try:
                # Disallows register under name which has been taken by other type of dataset
                # TODO: move the check to service side
                old_type = _restclient(workspace).dataset.get_dataset_by_name(
                    workspace.subscription_id,
                    workspace.resource_group,
                    workspace.name,
                    dataset_name=name,
                    include_latest_definition=False,
                    custom_headers=_custom_headers).dataset_type
                if old_type != new_dto.dataset_type:
                    raise Exception((
                        'There is already a "{}" dataset registered under name "{}". ' +
                        'Cannot register dataset of type "{}" under the same name.')
                        .format(
                            'legacy' if old_type is None or len(old_type) == 0 else old_type,
                            name,
                            new_dto.dataset_type))
            except HttpOperationError as e:
                if e.response.status_code != 404:
                    raise e  # TODO: log unknown exception
        try:
            registered_dto = _restclient(workspace).dataset.register(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_dto=new_dto,
                if_exists_ok=create_new_version,
                update_definition_if_exists=create_new_version,
                custom_headers=_custom_headers)

            version = registered_dto.latest.version_id
            try:
                version = int(version)
            except ValueError:
                version = None

            return self.__class__._create(
                definition=self._definition,
                registration=_DatasetRegistration(
                    workspace=workspace, name=registered_dto.name, version=version,
                    description=registered_dto.description, tags=registered_dto.tags))
        except HttpOperationError as e:
            if e.response.status_code == 409:
                raise Exception((
                    'There is already a dataset registered under name "{}". ' +
                    'Specify `create_new_version=True` to register the dataset as a new version.')
                    .format(name))
            else:
                raise e  # TODO: log unknown exception

    @classmethod
    @track(_get_logger)
    def _create(cls, definition, registration=None):
        if registration is not None and not isinstance(registration, _DatasetRegistration):
            raise TypeError('registration must be instance of `_DatasetRegistration`')
        dataset = cls()
        dataset._definition = definition
        dataset._registration = registration
        return dataset

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __str__(self):
        """Formats the dataset object into a string.

        :return: Returns string representation of the the dataset object
        :rtype: str
        """
        steps = self._dataflow._get_steps()
        step_type_pattern = re.compile(r'Microsoft.DPrep.(.*)Block', re.IGNORECASE)
        step_type = steps[0].step_type
        step_arguments = steps[0].arguments

        if hasattr(step_arguments, 'to_pod'):
            step_arguments = step_arguments.to_pod()
        if step_type == 'Microsoft.DPrep.GetDatastoreFilesBlock':
            source = step_arguments
        elif step_type == 'Microsoft.DPrep.GetFilesBlock':
            source = step_arguments['path']['resourceDetails']
        else:
            source = None

        encoder = dataprep().api.engineapi.typedefinitions.CustomEncoder \
            if hasattr(dataprep().api.engineapi.typedefinitions, 'CustomEncoder') \
            else dataprep().api.engineapi.engine.CustomEncoder
        return '{}\n{}'.format(
            type(self).__name__,
            json.dumps({
                'source': source,
                'definition': [
                    step_type_pattern.search(s.step_type).group(1) for s in steps
                ],
                'registration': None if self._registration is None else {
                    'name': self.name,
                    'version': self.version,
                    'description': self.description,
                    'tags': self.tags,
                    'id': self.id,
                    'workspaceName': self._registration.workspace.name,
                    'resourceGroup': self._registration.workspace.resource_group,
                    'subscription': self._registration.workspace.subscription_id
                }
            }, indent=2, cls=encoder))

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __repr__(self):
        """Formats the dataset object into a string.

        :return: Returns string representation of the the dataset object
        :rtype: str
        """
        return self.__str__()


class _DatasetRegistration(object):
    def __init__(self, workspace=None, id=None, name=None, version=None, description=None, tags=None):
        self.workspace = workspace
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.tags = tags


_custom_headers = {'x-ms-client-session-id': _ClientSessionId}
