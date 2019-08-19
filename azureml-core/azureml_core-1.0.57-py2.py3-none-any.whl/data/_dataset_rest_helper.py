# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for dataset service REST APIs."""

import os
from msrest.authentication import BasicTokenAuthentication
from azureml.data.constants import _DATASET_TYPE_TABULAR, _DATASET_TYPE_FILE
from azureml.data._loggerfactory import _LoggerFactory
from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._restclient.models.dataset_state_dto import DatasetStateDto
from azureml._restclient.models.dataset_definition_dto import DatasetDefinitionDto
from azureml._restclient.models.dataset_dto import DatasetDto
from azureml._restclient.rest_client import RestClient


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _dataset_to_dto(dataset, name, description=None, tags=None):
    from azureml.data.tabular_dataset import TabularDataset
    from azureml.data._dataset_client import _DatasetClient

    if isinstance(dataset, TabularDataset):
        dataset_type = _DATASET_TYPE_TABULAR
    else:
        raise RuntimeError('Unrecognized dataset type" {}'.format(type(dataset)))

    # keep old Dataset client which relies on file_type working
    file_type = _DatasetClient._get_source_file_type(dataset._dataflow)

    dataset_definition_dto = DatasetDefinitionDto(
        dataflow=dataset._dataflow.to_json(),
        dataset_definition_state=DatasetStateDto(),
        file_type=file_type)

    return DatasetDto(
        name=name,
        dataset_type=dataset_type,
        latest=dataset_definition_dto,
        description=description,
        tags=tags,
        is_visible=True)


def _dto_to_dataset(workspace, dto):
    if not isinstance(dto, DatasetDto):
        raise RuntimeError('dto has to be instance of DatasetDto')

    from azureml.data.tabular_dataset import TabularDataset
    from azureml.data._dataset import _DatasetRegistration

    version = dto.latest.version_id
    try:
        version = int(version)
    except ValueError:
        version = None
    registration = _DatasetRegistration(
        workspace=workspace, id=dto.dataset_id, name=dto.name, version=version,
        description=dto.description, tags=dto.tags)

    dataflow_json = dto.latest.dataflow
    if dataflow_json is None or len(dataflow_json) == 0:
        raise RuntimeError('Dataset without a definition cannot be migrated right now.')

    if dto.dataset_type == _DATASET_TYPE_TABULAR or not dto.dataset_type:
        # migrate legacy dataset which has dataflow to TabularDataset
        return TabularDataset._create(
            definition=dataflow_json,
            registration=registration)
    if dto.dataset_type == _DATASET_TYPE_FILE:
        raise RuntimeError('FileDataset is currently not supported.')
    raise RuntimeError('Unrecognized dataset type" {}'.format(dto.dataset_type))


def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
    return ('/subscriptions/{}/resourceGroups/{}/providers'
            '/Microsoft.MachineLearningServices'
            '/workspaces/{}').format(subscription_id, resource_group, workspace_name)


def _restclient(ws):
    host_env = os.environ.get('AZUREML_SERVICE_ENDPOINT')
    auth = ws._auth
    host = host_env or get_service_url(
        auth,
        _get_workspace_uri_path(
            ws._subscription_id,
            ws._resource_group,
            ws._workspace_name),
        ws._workspace_id)

    auth_header = ws._auth.get_authentication_header()['Authorization']
    access_token = auth_header[7:]  # 7 == len('Bearer ')

    return RestClient(base_url=host, credentials=BasicTokenAuthentication({
        'access_token': access_token
    }))
