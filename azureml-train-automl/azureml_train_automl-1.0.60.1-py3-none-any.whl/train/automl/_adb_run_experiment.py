# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class that runs automl run on ADB worker node."""
import datetime
import hashlib
import json
import logging
import os
import traceback
from typing import cast, Union, Any, List, Optional

import gc
from azureml._base_sdk_common.service_discovery import HISTORY_SERVICE_ENDPOINT_KEY
from azureml._restclient import JasmineClient
from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.service_context import ServiceContext
from azureml.core import Run
from azureml.core.authentication import AzureMLTokenAuthentication
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.telemetry import set_diagnostics_collection

from automl.client.core.common import logging_utilities as log_utils
from automl.client.core.common import utilities
from automl.client.core.common.cache_store import CacheStore
from automl.client.core.common.datasets import ClientDatasets
from azureml.automl.core import data_transformation
from azureml.automl.core import fit_pipeline as fit_pipeline_helper
from azureml.automl.core import training_utilities
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.data_context import RawDataContext, TransformedDataContext
from azureml.automl.core.faults_verifier import VerifierManager
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.train.automl._amlloguploader import _AMLLogUploader
from . import _logging
from . import constants
from ._adb_get_data import get_input_datamodel_from_dataprep_json, _input_data_model
from ._automl import _set_problem_info
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._cachestorefactory import CacheStoreFactory
from ._execute_with_retry import ExecuteWithRetry

MAX_RETRY_COUNT_ON_EXCEPTION = 5
BACK_OFF_FACTOR = 2
MAX_RETRY_COUNT_DURING_SETUP = 10000
MAX_WAIT_IN_SECONDS = 300
SLEEP_TIME = 10
JASMINE_CLIENT = "JasmineClient"
EXPERIMENT_CLIENT = "ExperimentClient"


def adb_run_experiment(input_params):
    """
    Read run configuration, get next pipeline, and call fit iteration.

    :param input_params: List of input parameters.
    :type input_params: list
    :return:
    :rtype: None
    """
    worker_id = input_params[0]
    run_context = input_params[1]
    subscription_id = run_context.get('subscription_id', None)
    resource_group = run_context.get('resource_group', None)
    workspace_name = run_context.get('workspace_name', None)
    location = run_context.get('location', None)
    aml_token = run_context.get('aml_token', None)
    aml_token_expiry = run_context.get('aml_token_expiry', None)
    experiment_name = run_context.get('experiment_name', None)
    parent_run_id = run_context.get('parent_run_id', None)
    service_url = run_context.get('service_url', None)
    dataprep_json = run_context.get('dataprep_json', None)
    automl_settings_str = run_context.get('automl_settings_str', None)
    _set_env_variables(subscription_id,
                       resource_group,
                       workspace_name,
                       experiment_name,
                       aml_token,
                       aml_token_expiry,
                       service_url)

    adb_experiment = _AdbAutomlExperiment(parent_run_id,
                                          subscription_id,
                                          resource_group,
                                          workspace_name,
                                          experiment_name,
                                          aml_token,
                                          aml_token_expiry,
                                          service_url,
                                          location,
                                          automl_settings_str,
                                          dataprep_json,
                                          worker_id)
    adb_experiment.Run()


def _set_env_variables(subscription_id, resource_group, workspace_name, experiment_name,
                       aml_token, aml_token_expiry, service_url):
    df_value_list = [subscription_id, resource_group, workspace_name, experiment_name,
                     aml_token, aml_token_expiry, service_url]
    var = None
    if any(var is None for var in df_value_list):
        raise ValueError("{0}: Value can't be None".format(var))
    os.environ["AZUREML_ARM_SUBSCRIPTION"] = subscription_id
    os.environ["AZUREML_ARM_RESOURCEGROUP"] = resource_group
    os.environ["AZUREML_ARM_WORKSPACE_NAME"] = workspace_name
    os.environ["AZUREML_ARM_PROJECT_NAME"] = experiment_name
    os.environ["AZUREML_RUN_TOKEN"] = aml_token
    os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(aml_token_expiry)
    os.environ["AZUREML_SERVICE_ENDPOINT"] = service_url


def log_message(logger=None, logging_level=logging.INFO, parent_run_id=None, worker_id=None, message=None):
    """
    Use to log messages.

    :param logger: The logger used to write message.
    :type logger: logging.Logger
    :param logging_level: The logging level to use.
    :type logging_level: str
    :param parent_run_id: The associated parent run ID.
    :type parent_run_id: str
    :param worker_id: The associated worker node ID.
    :type worker_id: str
    :param message: The associated message.
    :type message: str
    :return:
    :rtype: None
    """
    print("{0}, {1}, {2}, {3}".format(datetime.datetime.utcnow(), parent_run_id, worker_id, message))

    if logger is None:
        return

    if logging_level == logging.ERROR:
        logger.error("{0}, {1}, {2}, {3}".format(parent_run_id, worker_id, message, traceback.format_exc()))
    elif logging_level == logging.DEBUG:
        logger.debug("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    elif logging_level == logging.WARNING:
        logger.warning("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    else:
        logger.info("{0}, {1}, {2}".format(parent_run_id, worker_id, message))


class _AdbAutomlExperiment():

    DATASET_CACHED_KEY = 'dataset_cached_object'

    def __init__(self,
                 parent_run_id,
                 subscription_id,
                 resource_group,
                 workspace_name,
                 experiment_name,
                 aml_token,
                 aml_token_expiry,
                 service_url,
                 location,
                 automl_settings_str,
                 dataprep_json,
                 worker_id):
        self.parent_run_id = parent_run_id
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.experiment_name = experiment_name
        self.aml_token = aml_token
        self.aml_token_expiry = aml_token_expiry
        self.service_url = service_url
        self.location = location
        self.worker_id = worker_id
        self.automl_settings_str = automl_settings_str
        self.dataset = None  # type: Optional[ClientDatasets]

        os.environ["AZUREML_RUN_TOKEN"] = self.aml_token
        os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(self.aml_token_expiry)

        self.experiment_client = self._create_client(EXPERIMENT_CLIENT)
        self.automl_settings = AzureAutoMLSettings(
            self._rehydrate_experiment(), **json.loads(self.automl_settings_str))
        print("{0}, {1}, {2}, Enabling telemetry with verbosity {3}".format(datetime.datetime.utcnow(),
                                                                            self.parent_run_id,
                                                                            self.worker_id,
                                                                            self.automl_settings.telemetry_verbosity))
        set_diagnostics_collection(send_diagnostics=self.automl_settings.send_telemetry,
                                   verbosity=self.automl_settings.telemetry_verbosity)
        self.logger = _logging.get_logger(
            self.automl_settings.debug_log, self.automl_settings.verbosity, self.automl_settings)
        self.logger.update_default_property('parent_run_id', self.parent_run_id)

        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.logger)
        self._usage_telemetry.start()

        self.dataprep_json = dataprep_json
        self.jasmine_client_exception_count = 0

        try:
            # Note that this is due to known issue in shap library
            # Until that issue is fixed this is temporary mitigation specific
            # to AzureDatabricks.
            import matplotlib as mpl
            mpl.use('AGG')
        except Exception as e:
            self.log_message(message="Failed set the matplot backend. {}".format(e), logging_level=logging.ERROR)

    def _should_retry(self, output, exception, current_retry):
        pipeline_dto = output
        if pipeline_dto is not None:
            # reset exception counter since we were able to establish connnection
            self.jasmine_client_exception_count = 0
            should_retry = ((pipeline_dto.pipeline_spec is None or pipeline_dto.pipeline_spec == '') and
                            not pipeline_dto.is_experiment_over)
            should_retry = (should_retry and
                            ((pipeline_dto.childrun_id is not None or pipeline_dto.childrun_id == '') and
                             not pipeline_dto.childrun_id.endswith("setup")))
            return (should_retry, BACK_OFF_FACTOR)
        elif exception is not None:
            self.jasmine_client_exception_count += 1
            if self.jasmine_client_exception_count == MAX_RETRY_COUNT_ON_EXCEPTION:
                return (False, BACK_OFF_FACTOR)

            return (True, BACK_OFF_FACTOR)

        return (False, BACK_OFF_FACTOR)

    def _get_next_pipeline(self):
        aml_token = os.environ["AZUREML_RUN_TOKEN"]
        log_message(logger=self.logger,
                    parent_run_id=self.parent_run_id,
                    worker_id=self.worker_id,
                    message="Creating new jasmine client using amltoken(hash): '{}'".format(
                        hashlib.sha1(aml_token.encode()).hexdigest()))
        jasmine_client = self._create_client(JASMINE_CLIENT)
        pipeline_dto = jasmine_client.get_next_pipeline(
            self.parent_run_id, self.worker_id)
        return pipeline_dto

    def log_message(self, message, logging_level=logging.DEBUG):
        log_message(logger=self.logger,
                    logging_level=logging_level,
                    parent_run_id=self.parent_run_id,
                    worker_id=self.worker_id,
                    message=message)

    def Run(self):

        parent_run_id = self.parent_run_id
        worker_id = self.worker_id
        logger = self.logger
        log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Starting experiment run on worker node...")

        try:
            while (True):
                execute_with_retry = ExecuteWithRetry(
                    MAX_RETRY_COUNT_DURING_SETUP,
                    MAX_WAIT_IN_SECONDS,
                    self._should_retry,
                    self.log_message,
                    "jasmine_client.get_next_pipeline()")
                pipeline_dto = execute_with_retry.execute(
                    self._get_next_pipeline)
                if pipeline_dto.is_experiment_over:
                    log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                                message="Experiment finished.")
                    break
                child_run_id = pipeline_dto.childrun_id
                self.logger.update_default_property('child_run_id', child_run_id)
                os.environ["AZUREML_RUN_ID"] = child_run_id
                self.fit_iteration(pipeline_dto, child_run_id)
        except Exception as e:
            log_message(logger=logger, logging_level=logging.ERROR, parent_run_id=parent_run_id,
                        worker_id=worker_id, message=e)
            raise
        finally:
            try:
                parent_run = self._rehydrate_run(parent_run_id)
                filename, file_extension = os.path.splitext(self.automl_settings.debug_log)
                if os.path.exists(self.automl_settings.debug_log):
                    if not self.automl_settings.debug_log.startswith("/dbfs"):
                        formatted_file_name = "logs/{0}_{1}_{2}{3}".format(
                            filename, str(worker_id),
                            datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ"),
                            file_extension)

                        parent_run.upload_file(formatted_file_name, self.automl_settings.debug_log)
            except Exception as e:
                log_message(logger=logger, logging_level=logging.WARNING, parent_run_id=parent_run_id,
                            worker_id=worker_id, message=e)

        log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Finished experiment run on worker node.")

    def _rehydrate_experiment(self):
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        workspace = Workspace(self.subscription_id,
                              self.resource_group, self.workspace_name,
                              auth=auth,
                              _location=self.location,
                              _disable_service_check=True)
        experiment = Experiment(workspace, self.experiment_name)
        return experiment

    def _rehydrate_run(self, run_id):
        return Run(self._rehydrate_experiment(), run_id)

    def fit_iteration(self, pipeline_dto, run_id):
        """
        Fit iteration method.

        :param pipeline_dto: Pipeline details to fit.
        :type pipeline_dto: PipelineDto
        :param run_id: run id.
        :type run_id: string
        """
        run_id = pipeline_dto.childrun_id
        pipeline_id = pipeline_dto.pipeline_id

        train_frac = 1.0
        if hasattr(pipeline_dto, 'training_percent'):
            train_frac = float(pipeline_dto.training_percent) / 100

        """
        # TODO: Fix pipeline spec logging (#438111)
        log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                    message="Received pipeline: {0} for run id '{1}'".format(pipeline_dto.pipeline_spec, run_id))
        """
        self.logger.info('Received pipeline ID {}'.format(pipeline_id))

        verifier = VerifierManager()

        # This is due to token expiry issue
        current_run = self._rehydrate_run(run_id)

        with _AMLLogUploader(current_run, self.worker_id):
            try:
                current_run.start()
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Starting childrun...".format(run_id))
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Execution path {1}".format(run_id, os.path.realpath(__file__)))
                if (run_id.endswith("setup")):
                    self.logger.info('Beginning AutoML ADB setup for run {}.'.format(run_id))
                    input_data = get_input_datamodel_from_dataprep_json(
                        self.dataprep_json, self.log_message, automl_settings=self.automl_settings, logger=self.logger,
                        verifier=verifier)

                    with self.logger.log_activity(self.logger, activity_name='validate_training_data'):
                        training_utilities.validate_training_data(
                            X=input_data.X,
                            y=input_data.y,
                            X_valid=input_data.X_valid,
                            y_valid=input_data.y_valid,
                            sample_weight=input_data.sample_weight,
                            sample_weight_valid=input_data.sample_weight_valid,
                            cv_splits_indices=input_data.cv_splits_indices,
                            automl_settings=self.automl_settings)

                    _X = input_data.X
                    _y = input_data.y
                    transformed_data_context = None
                    cache_store = self._get_cache_store()
                    self.logger.info('Using {} for caching transformed data.'.format(type(cache_store).__name__))
                    if (self.automl_settings.enable_cache is True or
                            self.automl_settings.preprocess or
                            self.automl_settings.is_timeseries):
                        transformed_data_context = self._get_transformed_data_context(input_data,
                                                                                      cache_store,
                                                                                      verifier)
                        # We have a featurized data set now, which means either we had caching enabled or the
                        # data needed pre-processing. Either way, we save the hard work done to transform the data
                        # on the Azure Blob Store cache / local disk, from where other worker nodes can download from.
                        self.dataset = training_utilities.init_client_dataset(
                            transformed_data_context=transformed_data_context,
                            cache_store=cache_store,
                            automl_settings=self.automl_settings,
                            remote=False,
                            init_all_stats=False,
                            keep_in_memory=False)
                        cache_store.set(self.DATASET_CACHED_KEY, self.dataset)
                        self.logger.info("Initialized ClientDatasets from transformed_data_context during setup.")

                        _X = transformed_data_context.X
                        _y = transformed_data_context.y

                    with self.logger.log_activity(self.logger, activity_name='_set_problem_info'):
                        # P.S. The set_problem_info method also featurizes the data.
                        _set_problem_info(X=_X,
                                          y=_y,
                                          automl_settings=self.automl_settings,
                                          current_run=current_run,
                                          transformed_data_context=transformed_data_context,
                                          cache_store=cache_store,
                                          is_adb_run=True,
                                          logger=self.logger)

                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="{0}: Cache {1}, set_problem_info completed ..".
                                format(run_id, self.automl_settings.enable_cache))

                    if verifier is not None:
                        parent_run = self._rehydrate_run(self.parent_run_id)
                        parent_run_context = AzureAutoMLRunContext(parent_run, False)
                        verifier.write_result_file(parent_run_context, self.logger)

                    # Setup's finished. Eagerly clean up the input and/or featurized data.
                    # The model iteration workers will either recreate the featurized data (cache=False)
                    # or load the data from the Azure Blob Store cache (cache=True)
                    _X = None
                    _y = None
                    self.clear_input_data([transformed_data_context, input_data])
                    self.logger.info('Setup for ADB run id {} finished successfully.'.format(run_id))
                else:
                    # worker node
                    self.logger.info('Beginning AutoML ADB model training for run {}.'.format(run_id))
                    # if transformed_data_context is not set and if cache is enabled and preprocess is set to true
                    # try to load from cache
                    cache_store = self._get_cache_store()

                    if (self.dataset is None or
                            self.automl_settings.enable_cache or
                            self.automl_settings.preprocess or
                            self.automl_settings.is_timeseries):
                        current_run.add_properties({'LoadedFromCache': str(self.automl_settings.enable_cache)})
                        self.dataset = self._load_data_from_cache(cache_store)

                    if self.dataset is None:
                        # No cached data available. Need to recreate the transformed data.
                        input_data = get_input_datamodel_from_dataprep_json(self.dataprep_json,
                                                                            self.log_message,
                                                                            automl_settings=self.automl_settings,
                                                                            logger=self.logger)
                        log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                    message="Transformed_data_context is none, using dprep for fit")
                        transformed_data_context = self._get_transformed_data_context(input_data,
                                                                                      cache_store,
                                                                                      verifier)
                        self.dataset = training_utilities.init_client_dataset(
                            transformed_data_context=transformed_data_context,
                            cache_store=cache_store,
                            automl_settings=self.automl_settings,
                            remote=False,
                            init_all_stats=False,
                            keep_in_memory=False)

                        self.logger.info(
                            "Initialized ClientDatasets object from transformed_data_context.. "
                            "dropping transformed_data_context.")
                        self.clear_input_data([transformed_data_context])

                    automl_run_context = AzureAutoMLRunContext(Run.get_context(), is_adb_run=True)
                    automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_dto.pipeline_spec, pipeline_id,
                                                     train_frac)

                    result = fit_pipeline_helper.fit_pipeline(
                        automl_pipeline=automl_pipeline,
                        automl_settings=self.automl_settings,
                        automl_run_context=automl_run_context,
                        remote=True,
                        logger=self.logger,
                        dataset=self.dataset)

                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="result : {0}".format(result))
                    if result.errors:
                        err_type = next(iter(result.errors))
                        exception_info = result.errors[err_type]
                        exception_obj = cast(BaseException, exception_info['exception'])
                        exception_tb = cast(str, exception_info['traceback'])
                        log_message(logger=self.logger, logging_level=logging.ERROR,
                                    parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                    message="exception : Type {0} InnerException {1}".format(
                                        err_type, str(exception_obj)))
                        log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                    worker_id=self.worker_id, message="traceback : Type {0} Traceback : {1}".
                                    format(err_type, exception_tb))
                        if exception_info['is_critical']:
                            raise exception_obj.with_traceback(exception_obj.__traceback__)

                    score = result.score
                    duration = result.actual_time
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Score: {0}".format(score))
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Duration: {0}".format(duration))

                current_run.complete()
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Childrun completed successfully.".format(run_id))

            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id, message=str(e))
                if current_run is not None:
                    current_run.fail(
                        error_details=utilities.build_run_failure_error_detail(e),
                        error_code=utilities.get_error_code(e))
                if (run_id.endswith("setup")):
                    try:
                        errors = {'errors': str({'exception': e})}
                        current_run.add_properties(errors)
                    except Exception as ex:
                        self.log_message(message="{}: Failed to add 'errors' properties to run due to exception - {}"
                                         .format(run_id, ex),
                                         logging_level=logging.ERROR)
                        pass
                    raise

    def _create_client(self, client_type):
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        os.environ[HISTORY_SERVICE_ENDPOINT_KEY] = self.service_url
        service_context = ServiceContext(self.subscription_id,
                                         self.resource_group,
                                         self.workspace_name,
                                         None,
                                         auth)
        if(client_type == JASMINE_CLIENT):
            return JasmineClient(service_context, self.experiment_name,
                                 user_agent=client_type)
        elif(client_type == EXPERIMENT_CLIENT):
            return ExperimentClient(service_context, self.experiment_name,
                                    user_agent=client_type)

    def _get_transformed_data_context(self,
                                      input_data: _input_data_model,
                                      cache_store: CacheStore,
                                      verifier: VerifierManager) -> TransformedDataContext:
        with self.logger.log_activity(self.logger, activity_name='_setup_cache'):
            try:
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Trying to setup cache")

                raw_data_context = RawDataContext(automl_settings_obj=self.automl_settings,
                                                  X=input_data.X,
                                                  y=input_data.y,
                                                  X_valid=input_data.X_valid,
                                                  y_valid=input_data.y_valid,
                                                  sample_weight=input_data.sample_weight,
                                                  sample_weight_valid=input_data.sample_weight_valid,
                                                  x_raw_column_names=input_data.x_raw_column_names,
                                                  cv_splits_indices=input_data.cv_splits_indices)

                with self.logger.log_activity(self.logger, activity_name='transform_data'):
                    transformed_data_context = data_transformation\
                        .transform_data(raw_data_context=raw_data_context,
                                        preprocess=self.automl_settings.preprocess,
                                        logger=self.logger,
                                        cache_store=cache_store,
                                        enable_feature_sweeping=self.automl_settings.enable_feature_sweeping,
                                        verifier=verifier)

                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Cache is setup")

                return transformed_data_context
            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id, message="Featurization failed with exception {0}".
                            format(e))
                raise e

    def _load_data_from_cache(self, cache_store: CacheStore) -> Optional[ClientDatasets]:
        with self.logger.log_activity(self.logger, activity_name='_load_data_from_cache'):
            try:
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Loading from cache")
                cache_store.load()
                dataset_dict = cache_store.get([self.DATASET_CACHED_KEY])
                if dataset_dict is not None:
                    return dataset_dict.get(self.DATASET_CACHED_KEY)
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Failed to load from cache, failed to find {} in cache_store.".
                            format(self.DATASET_CACHED_KEY))
                return None
            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id,
                            message="Continuing without cache as trying to load from cache failed with exception {0}".
                            format(e))
                return None

    def _get_cache_store(self):
        data_store = self._get_data_store()

        cache_location = '{0}/{1}'.format(constants.ADBCACHEDIRECTORY, self.parent_run_id)

        os.makedirs(cache_location, exist_ok=True)
        return CacheStoreFactory.get_cache_store(enable_cache=True,
                                                 run_target='adb',
                                                 run_id=self.parent_run_id,
                                                 temp_location=cache_location,
                                                 logger=self.logger,
                                                 data_store=data_store)

    def _get_data_store(self):
        try:
            experiment = self._rehydrate_experiment()
            return experiment.workspace.get_default_datastore()
        except Exception as e:
            log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                        worker_id=self.worker_id,
                        message="No default data store found {0}".
                        format(e))
            return None

    def __del__(self):
        """
        Clean up AutoML loggers and close files.
        """
        log_utils.cleanup_log_map(self.automl_settings.debug_log,
                                  self.automl_settings.verbosity)

        if self._usage_telemetry is not None:
            self._usage_telemetry.stop()

    def clear_input_data(self, input_data_list: List[Union[TransformedDataContext, Any]]) -> None:
        for input_data in input_data_list:
            if input_data is not None:
                input_data.X = None
                input_data.y = None
                input_data.X_valid = None
                input_data.y_valid = None
                if isinstance(input_data, TransformedDataContext):
                    input_data.cv_splits = None
                self._gc_object(input_data)

    def _gc_object(self, obj):
        if obj is not None:
            del obj
            gc.collect()
