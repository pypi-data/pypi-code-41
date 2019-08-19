# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path, listdir
import logging
import ruamel.yaml

from azureml.core._experiment_method import experiment_method
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute import AmlCompute
from azureml.exceptions import TrainingException
from azureml.train._estimator_helper import _estimator_submit_method, _init_run_config, \
    _is_notebook_run, _update_config_for_notebook_run, _is_user_managed_environment
from ._mml_base_estimator import MMLBaseEstimator

module_logger = logging.getLogger(__name__)


class _FrameworkBaseEstimator(MMLBaseEstimator):
    """_FrameworkBaseEstimator is the base class of machine learning framework estimators."""

    _ACR_ADDRESS = 'viennaprivate.azurecr.io'
    _UNSUPPORTED_FRAMEWORK_VERSION_ERROR = \
        '{name} {version} is not currently supported by the {name} estimator. ' \
        'Check https://docs.microsoft.com/python/api/azureml-train-core/azureml.train.dnn?view=azure-ml-py ' \
        'for all supported versions. To use {name} {version}, switch to the generic Estimator class for your ' \
        'experiment.'
    _SCENARIO_FILE_NOT_FOUND_ERROR = 'Scenario file for {name}:{version} not found.'
    _EMPTY_FRAMEWORK_VERSION_WARNING = 'framework_version is not specified, defaulting to version {}.'
    _OPTIMIZED_MODE_PREVIEW_NOTICE = 'Note: Optimized Mode has been enabled. When additional packages are ' \
                                     'provided, pre-built framework image instead of default base image will ' \
                                     'be used as an intermediate image to build the final environment. '\
                                     'You can expect faster image building with this mode turned on. '\
                                     'This feature is currently in private preview.'

    FRAMEWORK_NAME = None
    DEFAULT_VERSION = None

    @experiment_method(submit_function=_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 compute_target=None,
                 vm_size=None,
                 vm_priority=None,
                 entry_script=None,
                 script_params=None,
                 node_count=1,
                 process_count_per_node=1,
                 distributed_backend=None,
                 distributed_training=None,
                 use_gpu=False,
                 use_docker=True,
                 custom_docker_image=None,
                 image_registry_details=None,
                 user_managed=False,
                 conda_packages=None,
                 pip_packages=None,
                 conda_dependencies_file_path=None,
                 pip_requirements_file_path=None,
                 conda_dependencies_file=None,
                 pip_requirements_file=None,
                 environment_variables=None,
                 environment_definition=None,
                 inputs=None,
                 source_directory_data_store=None,
                 shm_size=None,
                 resume_from=None,
                 max_run_duration_seconds=None,
                 framework_name=None,
                 framework_version=None,
                 _enable_optimized_mode=False):
        """Initialize the estimator.

        :param source_directory: A local directory containing experiment configuration and code files needed for a
            training job.
        :type source_directory: str
        :param compute_target:  The compute target where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param vm_size: The VM size of the compute target that will be created for the training.

            Supported values: Any `Azure VM size
            <https://docs.microsoft.com/azure/cloud-services/cloud-services-sizes-specs>`_.
        :type vm_size: str
        :param vm_priority: The VM priority of the compute target that will be created for the training. If not
            specified, 'dedicated' is used.

            Supported values: 'dedicated' and 'lowpriority'.

            This takes effect only when the ``vm_size`` param is specified in the input.
        :type vm_priority: str
        :param entry_script: The relative path to the file used to start training.
        :type entry_script: str
        :param script_params: A dictionary of command-line arguments to pass to the training script specified in
           ``entry_script``.
        :type script_params: dict
        :param node_count: The number of nodes in the compute target used for training. If greater than 1, a MPI
            distributed job will be run. Only the azureml.core.compute.AmlCompute target is supported for
            distributed jobs.
        :type node_count: int
        :param process_count_per_node: The number of processes per node. If greater than 1, a MPI
             distributed job will be run. Only AmlCompute target is supported for distributed jobs.
        :type process_count_per_node: int
        :param distributed_backend: The communication backend for distributed training.

            Supported values: 'mpi' and 'ps'.

                'mpi': MPI/Horovod
                'ps': parameter server

            This parameter is required when any of ``node_count``, ``process_count_per_node``, ``worker_count``, or
            ``parameter_server_count`` > 1.
            In case of 'ps', worker_count + parameter_server_count should be less than or equal to
            node_count * (number of CPUs or GPUs per node)

            When ``node_count`` == 1 and ``process_count_per_node`` == 1, no backend will be used
            unless the backend is explicitly set. Only the azureml.core.compute.AmlCompute target is supported for
            distributed training.
        :type distributed_backend: str
        :param distributed_training: Parameters for running a distributed training job. Use this parameter
            instead of the deprecated ``distributed_backend`` parameter.

            For running a distributed job with Parameter Server backend, use
            :class:`azureml.core.runconfig.TensorflowConfiguration` object to
            specify the ``worker_count`` and ``parameter_server_count`` parameters..
            The sum of ``worker_count`` and ``parameter_server_count`` should be less than or equal to
            ``node_count`` * (number of CPUs or GPUs per node).

            For running a distributed job with MPI backend, use :class:`azureml.core.runconfig.MpiConfiguration`
            object to specify ``process_count_per_node``.
        :type distributed_training: azureml.core.runconfig.TensorflowConfiguration or
            azureml.core.runconfig.MpiConfiguration
        :param use_gpu: Specifies whether the environment to run the experiment should support GPUs.
            If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
            image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
            parameter is not set. This setting is used only in Docker-enabled compute targets.
        :type use_gpu: bool
        :param use_docker: Specifies whether the environment to run the experiment should be Docker-based.
        :type use_docker: bool
        :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
        :type custom_docker_image: str
        :param image_registry_details: The details of the Docker image registry.
        :type image_registry_details: azureml.core.container_registry.ContainerRegistry
        :param user_managed: Specifies whether Azure ML reuses an existing Python environment. If false,
            means a Python environment is created based on the conda dependencies specification.
        :type user_managed: bool
        :param conda_packages: A list of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: A list of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param conda_dependencies_file_path: The relative path to the conda dependencies
            yaml file.
        :type conda_dependencies_file_path: str
        :param pip_requirements_file_path: The relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file_path: str
         :param conda_dependencies_file: The relative path to the conda dependencies
            yaml file.
        :type conda_dependencies_file: str
        :param pip_requirements_file: The relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file: str
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the process where user script is being executed.
        :type environment_variables: dict
        :param environment_definition: The environment definition for the experiment. It includes
            PythonSection, DockerSection, and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using this
            parameter. If this parameter is specified, it will take precedence over other environment-related
            parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages``.
            Errors will be reported on these invalid combinations.
        :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
        :param inputs: A list of azureml.data.data_reference.DataReference objects to use as input.
        :type inputs: list
        :param source_directory_data_store: The backing data store for the project share.
        :type source_directory_data_store: azureml.core.Datastore
        :param shm_size: The size of the Docker container's shared memory block. If not set, the default
        azureml.core.environment._DEFAULT_SHM_SIZE is used. For more information, see
        `Docker run reference <https://docs.docker.com/engine/reference/run/>`_.
        :type shm_size: str
        :param resume_from: The data path containing the checkpoint or model files from which to resume the experiment.
        :type resume_from: azureml.data.datapath.DataPath
        :param max_run_duration_seconds: The maximum allowed time for the run. Azure ML will attempt to automatically
            cancel the run if it takes longer than this value.
        :type max_run_duration_seconds: int
        :param framework_name: The name of the framework to be used for the estimator.
        :type framework_name: str
        :param framework_version: The version of the framework to be used for the estimator.
        :type framework_version: str
        :param _enable_optimized_mode: Enable incremental environment build with pre-built framework images for faster
            environment preparation. A pre-built framework image is built on top of Azure ML default CPU/GPU base
            images with framework dependencies pre-installed.
        :type _enable_optimized_mode: bool
        """
        # For deprecation purposes
        if conda_dependencies_file:
            conda_output_str = "conda_dependencies_file"
        else:
            conda_output_str = "conda_dependencies_file_path"

        if environment_definition or (conda_dependencies_file_path or conda_dependencies_file):
            module_logger.warning("If environment_definition or {} is specified, Azure ML "
                                  "will not install any framework related packages on behalf of "
                                  "the user.".format(conda_output_str))

        self._optimized_mode = _enable_optimized_mode
        if self._optimized_mode:
            module_logger.warning(self._OPTIMIZED_MODE_PREVIEW_NOTICE)

        self._use_framework_image = False
        self._framework_name = framework_name if framework_name is not None else self.FRAMEWORK_NAME
        self._framework_version = framework_version

        self._estimator_config = \
            _init_run_config(estimator=self, source_directory=source_directory, compute_target=compute_target,
                             vm_size=vm_size, vm_priority=vm_priority, entry_script=entry_script,
                             script_params=script_params, node_count=node_count,
                             process_count_per_node=process_count_per_node, distributed_backend=distributed_backend,
                             distributed_training=distributed_training, use_gpu=use_gpu, use_docker=use_docker,
                             custom_docker_image=custom_docker_image, image_registry_details=image_registry_details,
                             user_managed=user_managed, conda_packages=conda_packages, pip_packages=pip_packages,
                             conda_dependencies_file_path=conda_dependencies_file_path,
                             pip_requirements_file_path=pip_requirements_file_path,
                             conda_dependencies_file=conda_dependencies_file,
                             pip_requirements_file=pip_requirements_file,
                             environment_variables=environment_variables,
                             environment_definition=environment_definition, inputs=inputs,
                             source_directory_data_store=source_directory_data_store, shm_size=shm_size,
                             resume_from=resume_from, max_run_duration_seconds=max_run_duration_seconds)

        if self.framework_version is None:
            self._framework_version = self.DEFAULT_VERSION
            if not self._estimator_config.environment.python.user_managed_dependencies and \
                    len(self.__class__.get_supported_versions()) > 1:
                module_logger.warning(self._EMPTY_FRAMEWORK_VERSION_WARNING.format(self.DEFAULT_VERSION))
        else:
            if framework_version not in self.__class__.get_supported_versions():
                raise TrainingException(self._UNSUPPORTED_FRAMEWORK_VERSION_ERROR.format(name=framework_name,
                                                                                         version=framework_version))

        if not conda_dependencies_file:
            conda_dependencies_file = conda_dependencies_file_path

        self._framework_processor = 'gpu' if self._estimator_config.environment.docker.gpu_support else 'cpu'
        self._manual_restart_used = (resume_from is not None)
        self._user_dependencies_provided = self.conda_dependencies.serialize_to_string() != \
            CondaDependencies().serialize_to_string()
        self._is_conflict_package_added = False

        if not _is_user_managed_environment(environment_definition):
            self._check_package_conflicts()
            self._setup_environment(custom_docker_image, compute_target, entry_script,
                                    environment_definition, conda_dependencies_file)

        self._distributed_backend = distributed_backend
        if distributed_training:
            self._distributed_backend = distributed_training

        if _is_notebook_run(entry_script):
            _update_config_for_notebook_run(self._estimator_config, use_gpu,
                                            custom_docker_image)

        super().__init__(source_directory, compute_target=compute_target,
                         estimator_config=self._estimator_config)

    @property
    def framework_version(self):
        """
        Return the framework version.

        :return: The framework version.
        :rtype: str
        """
        return self._framework_version

    def _get_telemetry_values(self, func):
        telemetry_values = super()._get_telemetry_values(func)
        telemetry_values['frameworkVersion'] = self._framework_version
        telemetry_values['frameworkImageUsed'] = self._use_framework_image
        telemetry_values['incrementalBuild'] = self._estimator_config.environment.python. \
            _base_conda_environment is not None
        telemetry_values['addCondaOrPipPackage'] = self._user_dependencies_provided
        telemetry_values['manualRestart'] = self._manual_restart_used
        telemetry_values['isConflictPackagesAdded'] = self._is_conflict_package_added
        return telemetry_values

    def _load_from_scenario_file(self):
        # TODO: move file not found and parse error checks to gated tests
        scenario_filename = '{}-{}-{}.yml'.format(self._framework_name,
                                                  self._framework_version,
                                                  self._framework_processor).lower()
        scenario_path = path.join(path.dirname(__file__), "scenarios", scenario_filename)
        if not path.isfile(scenario_path):
            raise TrainingException((self._SCENARIO_FILE_NOT_FOUND_ERROR).
                                    format(name=self._framework_name, version=self._framework_version))
        with open(scenario_path, "r") as input:
            scenario = ruamel.yaml.round_trip_load(input)
            base_image = scenario.get('baseImage', None)
            dependencies = scenario.get('inlineCondaDependencies', None)

        return base_image, CondaDependencies(_underlying_structure=dependencies)

    def _setup_environment(self, custom_docker_image, compute_target, entry_script, environment_definition,
                           conda_dependencies_file):
        # check if framework image can be used
        self._use_framework_image = self._optimized_mode or not self._user_dependencies_provided

        if compute_target and not isinstance(compute_target, AmlCompute):
            self._use_framework_image = False
            if self._optimized_mode:
                raise TrainingException("Optimized mode is not supported for non-AmlCompute targets.")
        if environment_definition is not None or custom_docker_image is not None:
            self._use_framework_image = False
            if self._optimized_mode:
                raise TrainingException("Optimized mode is not supported when environment_definition "
                                        "or custom_docker_image is provided.")
        # Notebook runs are supported only in OpenMPI base images.
        # Current framework images use IntelMPI so they cannot be used.
        # Also, a full build is needed to install papermill dependencies.
        if _is_notebook_run(entry_script):
            self._use_framework_image = False
            if self._optimized_mode:
                raise TrainingException("Optimized mode is not supported when entry_script is a notebook "
                                        "file(.ipynb).")

        # setup the environment
        if self._use_framework_image:
            framework_image = '{}:{}-{}'.format(self._framework_name.lower(),
                                                self._framework_version,
                                                self._framework_processor)
            self._estimator_config.environment.docker.base_image = framework_image
            self._estimator_config.environment.docker.base_image_registry.address = self._ACR_ADDRESS
            if not self._user_dependencies_provided:
                # 1) no build - use framework image as final image
                self._estimator_config.environment.python.user_managed_dependencies = True
            else:
                # 2) incremental build - use framework image as base image
                self._estimator_config.environment.python._base_conda_environment = 'base'
        elif not environment_definition:
            # 3) full build
            default_base_image, framework_dependencies = self._load_from_scenario_file()
            # if conda_dependencies_file is specified, don't add framework dependencies
            if conda_dependencies_file is None:
                self.conda_dependencies._merge_dependencies(framework_dependencies)
            # if custom_docker_image or environment_definition is specified, don't override base image
            if custom_docker_image is None:
                self._estimator_config.environment.docker.base_image = default_base_image

    def _check_package_conflicts(self):
        self._is_conflict_package_added = False
        # Check if there are duplicate between packages that Azure ML installs and user specified packages.
        default_base_image, framework_dependencies = self._load_from_scenario_file()

        # Get all framework related packages installed by Azure ML
        # This will have default CondaDependencies() packages like azureml-defaults and framework related packages.
        framework_packages = []
        framework_packages.extend(
            [framework_dependencies._get_package_name(x) for x in framework_dependencies.pip_packages])
        framework_packages.extend(
            [framework_dependencies._get_package_name(x) for x in framework_dependencies.conda_packages])

        # Get all packages in estimator
        # This will have default CondaDependencies() packages like azureml-defaults and user specified packages.
        estimator_packages = []
        estimator_packages.extend(
            [self.conda_dependencies._get_package_name(x) for x in self.conda_dependencies.pip_packages])
        estimator_packages.extend(
            [self.conda_dependencies._get_package_name(x) for x in self.conda_dependencies.conda_packages])

        # Get default packages
        # This will help remove common packages between framework_packages and estimator_packages that
        # came from default CondaDependcies().
        default_packages = []
        default_packages.extend(
            [CondaDependencies()._get_package_name(x) for x in CondaDependencies().pip_packages])
        default_packages.extend(
            [CondaDependencies()._get_package_name(x) for x in CondaDependencies().conda_packages])

        common_packages = [p for p in estimator_packages if p in framework_packages and p not in default_packages]

        if len(common_packages):
            module_logger.warning("You have specified to install packages in your run. "
                                  "Note that Azure ML also installs the following packages on your behalf: {}. \n"
                                  "This may lead to unexpected package installation errors. "
                                  "Take a look at `estimator.conda_dependencies` to understand what packages are "
                                  "installed by Azure ML.".format([p for p in common_packages]))
            self._is_conflict_package_added = True

    @classmethod
    def get_supported_versions(cls):
        """
        Return the framework versions supported by the current SDK.

        :return: The supported framework versions.
        :rtype: list
        """
        framework_dir = path.join(path.dirname(__file__), "scenarios")
        dir_list = listdir(framework_dir)
        supported_versions = set([])

        for scenario_file in dir_list:
            if scenario_file.startswith(cls.FRAMEWORK_NAME.lower()):
                version = scenario_file.split('-')[1]
                supported_versions.add(version)

        return sorted(list(supported_versions))
