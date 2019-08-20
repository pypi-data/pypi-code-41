# Copyright (c) Microsoft Corporation. All rights reserved.
# pylint: skip-file
# This file is auto-generated. Do not modify.
from typing import List, Dict
from uuid import UUID
from .enginerequests import EngineRequestsChannel
from .engine import launch_engine, CancellationToken
from . import typedefinitions
from .._aml_helper import update_aml_env_vars


_engine_api = None


def get_engine_api():
    global _engine_api
    if not _engine_api:
        _engine_api = EngineAPI()

        from .._dataset_resolver import register_dataset_resolver
        register_dataset_resolver(_engine_api.requests_channel)

        from ..sparkexecution import _ensure_interactive_spark
        _ensure_interactive_spark(_engine_api.requests_channel)

        from .._dataframereader import ensure_dataframe_reader_handlers
        ensure_dataframe_reader_handlers(_engine_api.requests_channel)
    return _engine_api


def kill_engine_api():
    global _engine_api
    if _engine_api:
        _engine_api._engine.close()
        _engine_api = None


class EngineAPI:
    def __init__(self):
        self._engine = launch_engine()
        self.requests_channel = EngineRequestsChannel(self)

    @update_aml_env_vars(get_engine_api)
    def add_block_to_list(self, message_args: typedefinitions.AddBlockToListMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.AnonymousBlockData:
        response = self._engine.send_message('Engine.AddBlockToList', message_args, cancellation_token)
        return typedefinitions.AnonymousBlockData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def add_temporary_secrets(self, message_args: Dict[str, str], cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.AddTemporarySecrets', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def anonymous_data_source_prose_suggestions(self, message_args: typedefinitions.AnonymousDataSourceProseSuggestionsMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.DataSourceProperties:
        response = self._engine.send_message('GetProseAnonymousDataSourcePropertiesSuggestion', message_args, cancellation_token)
        return typedefinitions.DataSourceProperties.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def anonymous_send_message_to_block(self, message_args: typedefinitions.AnonymousSendMessageToBlockMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.AnonymousSendMessageToBlockMessageResponseData:
        response = self._engine.send_message('Engine.SendMessageToBlock', message_args, cancellation_token)
        return typedefinitions.AnonymousSendMessageToBlockMessageResponseData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def close_stream_info(self, message_args: str, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.CloseStreamInfo', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def create_anonymous_reference(self, message_args: typedefinitions.CreateAnonymousReferenceMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.ActivityReference:
        response = self._engine.send_message('Engine.CreateAnonymousReference', message_args, cancellation_token)
        return typedefinitions.ActivityReference.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def download_stream_info(self, message_args: typedefinitions.DownloadStreamInfoMessageArguments, cancellation_token: CancellationToken = None) -> int:
        response = self._engine.send_message('Engine.DownloadStreamInfo', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def execute_anonymous_blocks(self, message_args: typedefinitions.ExecuteAnonymousBlocksMessageArguments, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.ExecuteActivity', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def execute_data_diff(self, message_args: typedefinitions.ExecuteDataDiffMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.ExecuteDataDiffMessageResponse:
        response = self._engine.send_message('Engine.ExecuteDataDiff', message_args, cancellation_token)
        return typedefinitions.ExecuteDataDiffMessageResponse.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def execute_inspector(self, message_args: typedefinitions.ExecuteInspectorCommonArguments, cancellation_token: CancellationToken = None) -> typedefinitions.ExecuteInspectorCommonResponse:
        response = self._engine.send_message('Engine.ExecuteInspector', message_args, cancellation_token)
        return typedefinitions.ExecuteInspectorCommonResponse.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def execute_inspectors(self, message_args: List[typedefinitions.ExecuteInspectorsMessageArguments], cancellation_token: CancellationToken = None) -> Dict[str, typedefinitions.ExecuteInspectorCommonResponse]:
        response = self._engine.send_message('Engine.ExecuteInspectors', message_args, cancellation_token)
        return {k: typedefinitions.ExecuteInspectorCommonResponse.from_pod(v) if v is not None else None for k, v in response.items()} if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def export_script(self, message_args: typedefinitions.ExportScriptMessageArguments, cancellation_token: CancellationToken = None) -> List[typedefinitions.SecretData]:
        response = self._engine.send_message('Project.ExportScript', message_args, cancellation_token)
        return [typedefinitions.SecretData.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_activity(self, message_args: str, cancellation_token: CancellationToken = None) -> typedefinitions.AnonymousActivityData:
        response = self._engine.send_message('Engine.GetActivity', message_args, cancellation_token)
        return typedefinitions.AnonymousActivityData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_block_descriptions(self, message_args: None, cancellation_token: CancellationToken = None) -> List[typedefinitions.IBlockDescription]:
        response = self._engine.send_message('Engine.GetBlockDescriptions', message_args, cancellation_token)
        return [typedefinitions.IBlockDescription.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_data(self, message_args: typedefinitions.GetDataMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.GetDataMessageResponse:
        response = self._engine.send_message('Engine.GetData', message_args, cancellation_token)
        return typedefinitions.GetDataMessageResponse.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_inspector_descriptions(self, message_args: None, cancellation_token: CancellationToken = None) -> List[typedefinitions.InspectorDescription]:
        response = self._engine.send_message('Engine.GetInspectorDescriptions', message_args, cancellation_token)
        return [typedefinitions.InspectorDescription.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_partition_count(self, message_args: List[typedefinitions.AnonymousBlockData], cancellation_token: CancellationToken = None) -> int:
        response = self._engine.send_message('Engine.GetPartitionCount', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def get_program_step_descriptions(self, message_args: None, cancellation_token: CancellationToken = None) -> List[typedefinitions.ProgramStepDescription]:
        response = self._engine.send_message('Engine.GetProgramStepDescriptions', message_args, cancellation_token)
        return [typedefinitions.ProgramStepDescription.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_secrets(self, message_args: typedefinitions.GetSecretsMessageArguments, cancellation_token: CancellationToken = None) -> List[typedefinitions.SecretData]:
        response = self._engine.send_message('Engine.GetSecrets', message_args, cancellation_token)
        return [typedefinitions.SecretData.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_source_data_hash(self, message_args: typedefinitions.GetSourceDataHashMessageArguments, cancellation_token: CancellationToken = None) -> str:
        response = self._engine.send_message('Engine.GetSourceDataHash', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def infer_types(self, message_args: List[typedefinitions.AnonymousBlockData], cancellation_token: CancellationToken = None) -> Dict[str, typedefinitions.FieldInference]:
        response = self._engine.send_message('Engine.InferTypes', message_args, cancellation_token)
        return {k: typedefinitions.FieldInference.from_pod(v) if v is not None else None for k, v in response.items()} if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def load_activity_from_json(self, message_args: str, cancellation_token: CancellationToken = None) -> typedefinitions.AnonymousActivityData:
        response = self._engine.send_message('Engine.LoadProjectFromJson', message_args, cancellation_token)
        return typedefinitions.AnonymousActivityData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def open_stream_info(self, message_args: typedefinitions.Value, cancellation_token: CancellationToken = None) -> str:
        response = self._engine.send_message('Engine.OpenStreamInfo', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def read_stream_info(self, message_args: typedefinitions.ReadStreamInfoMessageArguments, cancellation_token: CancellationToken = None) -> int:
        response = self._engine.send_message('Engine.ReadStreamInfo', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def register_secret(self, message_args: typedefinitions.RegisterSecretMessageArguments, cancellation_token: CancellationToken = None) -> typedefinitions.Secret:
        response = self._engine.send_message('SecretManager.RegisterSecret', message_args, cancellation_token)
        return typedefinitions.Secret.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def save_activity_from_data(self, message_args: typedefinitions.SaveActivityFromDataMessageArguments, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Project.SaveAnonymous', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def save_activity_to_json(self, message_args: typedefinitions.AnonymousActivityData, cancellation_token: CancellationToken = None) -> str:
        response = self._engine.send_message('Project.SaveAnonymousToJson', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_aml_auth(self, message_args: typedefinitions.SetAmlAuthMessageArgument, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.SetAmlAuth', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_executor(self, message_args: typedefinitions.ExecutorType, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.SetExecutor', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_host_channel_port(self, message_args: int, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.SetHostChannelPort', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_host_secret(self, message_args: str, cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.SetHostSecret', message_args, cancellation_token)
        return response

    @update_aml_env_vars(get_engine_api)
    def update_environment_variable(self, message_args: Dict[str, str], cancellation_token: CancellationToken = None) -> None:
        response = self._engine.send_message('Engine.UpdateEnvironmentVariable', message_args, cancellation_token)
        return response
