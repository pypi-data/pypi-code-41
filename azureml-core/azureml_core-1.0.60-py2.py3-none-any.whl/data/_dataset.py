# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Abstract Dataset class."""

from abc import ABCMeta
import collections
import re
import json

from msrest.exceptions import HttpOperationError
from azureml._base_sdk_common import _ClientSessionId
from azureml.data.dataset_factory import TabularDatasetFactory, FileDatasetFactory
from azureml.data.constants import _DATASET_TYPE_TABULAR
from azureml.data._dataprep_helper import dataprep
from azureml.data._dataset_rest_helper import _dto_to_dataset, _dataset_to_dto, _dataset_to_saved_dataset_dto, \
    _saved_dataset_dto_to_dataset, _restclient, _resolve_dataset_type
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
    File = FileDatasetFactory

    def __init__(self):
        """Class _Dataset constructor.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class and
        :class:`azureml.data.dataset_factory.FileDatasetFactory` class.
        """
        if self.__class__ == _Dataset:
            raise RuntimeError('Cannot create instance of absctract class _Dataset')
        self._definition = None
        self._properties = None
        self._registration = None

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_by_name(workspace, name, version='latest'):
        """Gets a registered Dataset from workspace by its registration name.

        :param workspace: The existing AzureML workspace in which the Dataset was registered.
        :type workspace: azureml.core.Workspace
        :param name: The registration name.
        :type name: str
        :param version: The registration version. Defaults to 'latest'.
        :type version: int
        :return: The registered dataset object.
        :rtype: azureml.data.TabularDataset or azureml.data.FileDataset
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

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_by_id(workspace, id):
        dto = _restclient(workspace).dataset.get_by_id(
            subscription_id=workspace.subscription_id, resource_group_name=workspace.resource_group,
            workspace_name=workspace.name, id=id
        )
        return _saved_dataset_dto_to_dataset(workspace, dto)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def get_all(workspace):
        """Get all the registered datasets in the workspace.

        :param workspace: The existing AzureML workspace in which the Datasets were registered.
        :type workspace: azureml.core.Workspace
        :return: A dictionary of TabularDataset and FileDataset objects keyed by their registration name.
        :rtype: dict[str, azureml.data.TabularDataset or azureml.data.FileDataset]
        """
        def list_dataset(continuation_token):
            return _restclient(workspace).dataset.list(
                subscription_id=workspace.subscription_id,
                resource_group_name=workspace.resource_group,
                workspace_name=workspace.name,
                page_size=100,
                include_latest_definition=False,
                include_invisible=False,
                continuation_token=continuation_token,
                custom_headers=_custom_headers)

        def get_dataset(name):
            try:
                return _Dataset.get_by_name(workspace, name)
            except Exception:
                return None

        return _DatasetDict(list_fn=list_dataset, get_fn=get_dataset)

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def id(self):
        """Return the registration id.

        :return: Dataset id.
        :rtype: str
        """
        if self._registration:
            if self._registration.id:
                return self._registration.id
            if self._registration.workspace:
                self._ensure_saved(self._registration.workspace)
                return self._registration.id
        return None

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def name(self):
        """Return the registration name.

        :return: Dataset name.
        :rtype: str
        """
        return None if self._registration is None else self._registration.name

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def version(self):
        """Return the registration version.

        :return: Dataset version.
        :rtype: str
        """
        return None if self._registration is None else self._registration.version

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def description(self):
        """Return the registration description.

        :return: Dataset description.
        :rtype: str
        """
        return None if self._registration is None else self._registration.description

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def tags(self):
        """Return the registration tags.

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
        :rtype: azureml.data.TabularDataset or azureml.data.FileDataset
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
                properties=self._properties,
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
    def _create(cls, definition, properties=None, registration=None):
        if registration is not None and not isinstance(registration, _DatasetRegistration):
            raise TypeError('registration must be instance of `_DatasetRegistration`')
        dataset = cls()
        dataset._definition = definition  # definition is either str or Dataflow which is immutable
        dataset._properties = properties.copy() if properties else {}  # shallow copy, assuming immutable values
        dataset._registration = registration
        return dataset

    @track(_get_logger)
    def _ensure_saved(self, workspace):
        dto = _restclient(workspace).dataset.ensure_saved(
            subscription_id=workspace.subscription_id, resource_group_name=workspace.resource_group,
            workspace_name=workspace.name, dataset=_dataset_to_saved_dataset_dto(self)
        )
        saved_dataset = _saved_dataset_dto_to_dataset(workspace, dto)
        if self._registration:
            self._registration.id = saved_dataset._registration.id
        else:
            self._registration = saved_dataset._registration

        return self._registration.id

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __str__(self):
        """Format the dataset object into a string.

        :return: Return string representation of the the dataset object
        :rtype: str
        """
        steps = self._dataflow._get_steps()
        step_type_pattern = re.compile(r'Microsoft.DPrep.(.*)Block', re.IGNORECASE)
        step_type = steps[0].step_type
        step_arguments = steps[0].arguments

        if hasattr(step_arguments, 'to_pod'):
            step_arguments = step_arguments.to_pod()
        if step_type == 'Microsoft.DPrep.GetDatastoreFilesBlock':
            source = [
                '(\'{}\', \'{}\')'.format(store['datastoreName'], store['path'])
                for store in step_arguments['datastores']
            ]
        elif step_type == 'Microsoft.DPrep.GetFilesBlock':
            source = [details['path'] for details in step_arguments['path']['resourceDetails']]
        else:
            source = None

        encoder = dataprep().api.engineapi.typedefinitions.CustomEncoder \
            if hasattr(dataprep().api.engineapi.typedefinitions, 'CustomEncoder') \
            else dataprep().api.engineapi.engine.CustomEncoder

        content = {
            'source': source,
            'definition': [
                step_type_pattern.search(s.step_type).group(1) for s in steps
            ]
        }
        if self._registration is not None:
            content['registration'] = {
                'name': self.name,
                'version': self.version
            }
            if self.description:
                content['registration']['description'] = self.description
            if self.tags:
                content['registration']['tags'] = self.tags
            content['registration']['workspace'] = self._registration.workspace.__repr__()

        return '{}\n{}'.format(type(self).__name__, json.dumps(content, indent=2, cls=encoder))

    @track(_get_logger, activity_type=_PUBLIC_API)
    def __repr__(self):
        """Format the dataset object into a string.

        :return: Return string representation of the the dataset object
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


_Mapping = collections.abc.Mapping if hasattr(collections, 'abc') else collections.Mapping


class _DatasetDict(_Mapping):
    def __init__(self, list_fn, get_fn):
        self._list_fn = list_fn
        self._get_fn = get_fn
        self._all_listed = False
        self._list_continuation_token = None
        self._list_cached = {}
        self._getitem_cached = {}

    def __getitem__(self, key):
        if key in self._getitem_cached:
            return self._getitem_cached[key]
        result = self._get_fn(name=key)
        if result is None:
            raise KeyError(key)
        self._getitem_cached[key] = result
        return result

    def __iter__(self):
        return iter(self._list_cached if self._all_listed else _DatasetDictKeyIterator(self))

    def __len__(self):
        while not self._all_listed:
            self._list_more()
        return len(self._list_cached)

    def __str__(self):
        while not self._all_listed:
            self._list_more()
        names = self._list_cached.keys()
        if not names:
            return '{}'
        longest = max(len(name) for name in names)
        content = '{'
        for name, registration in self._list_cached.items():
            ds_type, desc, tags = registration
            content += '\'{}\':{}{}('.format(
                name,
                ' ' * (1 + longest - len(name)),
                'TabularDataset' if ds_type == _DATASET_TYPE_TABULAR else 'FileDataset')
            if desc:
                content += 'description={}'.format(desc.__repr__())
                if tags:
                    content += ', '
            if tags:
                content += 'tags={}'.format(tags)
            content += '),\n '
        content = content[:-3] + '}'
        return content

    def __repr__(self):
        return self.__str__()

    def _list_more(self):
        new_listed_names = []
        if not self._all_listed:
            list_result = self._list_fn(continuation_token=self._list_continuation_token)
            if list_result.continuation_token is None:
                self._all_listed = True
            else:
                self._list_continuation_token = list_result.continuation_token
            for ds in list_result.value:
                if ds is not None:
                    self._list_cached[ds.name] = (_resolve_dataset_type(ds.dataset_type), ds.description, ds.tags)
                    new_listed_names.append(ds.name)
        return new_listed_names


class _DatasetDictKeyIterator():
    def __init__(self, ds_dict):
        self._ds_dict = ds_dict
        self._pending_keys = list(ds_dict._list_cached.keys())

    def __iter__(self):
        return self

    def __next__(self):
        if self._ds_dict._all_listed and not self._pending_keys == 0:
            raise StopIteration
        if not self._pending_keys:
            self._pending_keys.extend(self._ds_dict._list_more())
        if not self._pending_keys:
            raise StopIteration
        return self._pending_keys.pop(0)


_custom_headers = {'x-ms-client-session-id': _ClientSessionId}
