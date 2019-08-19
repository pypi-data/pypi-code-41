# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""pipeline.py, module for creating and submitting a pipeline."""
from azureml.pipeline.core._graph_context import _GraphContext
from azureml.pipeline.core.builder import _PipelineGraphBuilder, PipelineData
from azureml.pipeline.core.graph import InputPortBinding, PipelineParameter, PipelineDataset
from azureml.pipeline.core.graph import StoredProcedureParameter, StoredProcedureParameterType
from azureml.pipeline.core.module import Module
from azureml.core import Datastore, Dataset, RunConfiguration
from azureml.core._experiment_method import experiment_method
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.data.data_reference import DataReference
from azureml.data.sql_data_reference import SqlDataReference
from azureml.pipeline.core.module_step_base import ModuleStepBase
import logging


_ARGUMENTS = 'arguments'
_ARGUMENT_INPUT = 'input:'
_ARGUMENT_OUTPUT = 'output:'
_ARGUMENT_PARAMETER = 'parameter:'
_BOOL = 'bool'
_COMPUTE = 'compute'
_DATAPATH = 'datapath'
_DATASTORE = 'datastore'
_DATA_REFERENCES = 'data_references'
_DATASET_ID = 'dataset_id'
_DATASET_NAME = 'dataset_name'
_DEFAULT = 'default'
_DEFAULT_COMPUTE = 'default_compute'
_DESTINATION = 'destination'
_DOWNLOAD = 'download'
_FLOAT = 'float'
_ID = 'id'
_INPUTS = 'inputs'
_INT = 'int'
_MODULE = 'module'
_MOUNT = 'mount'
_NAME = 'name'
_OUTPUTS = 'outputs'
_OVERWRITE = 'overwrite'
_PARAMETERS = 'parameters'
_PATH_ON_COMPUTE = 'path_on_compute'
_PIPELINE = 'pipeline'
_PATH_ON_DATASTORE = 'path_on_datastore'
_RUNCONFIG = 'runconfig'
_RUNCONFIG_PARAMETERS = 'runconfig_parameters'
_SOURCE = 'source'
_STEPS = 'steps'
_STRING = 'string'
_SQL_TABLE = 'sql_table'
_SQL_QUERY = 'sql_query'
_SQL_STORED_PROCEDURE = 'sql_stored_procedure'
_SQL_STORED_PROCEDURE_PARAMS = 'sql_stored_procedure_params'
_TYPE = 'type'
_UPLOAD = 'upload'
_VERSION = 'version'
_VALUE = 'value'


def _submit_pipeline(pipeline, workspace, experiment_name, **kwargs):
    """
    Submit a pipeline.

    :param pipeline: pipeline
    :type pipeline: Pipeline
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    continue_on_step_failure = False
    regenerate_outputs = False
    pipeline_params = None
    parent_run_id = None
    for key, value in kwargs.items():
        if key == 'continue_on_step_failure':
            continue_on_step_failure = value
        elif key == 'regenerate_outputs':
            regenerate_outputs = value
        elif key == 'pipeline_params':
            pipeline_params = value
            logging.warning(
                "The 'pipeline_params' argument is deprecated. Please use 'pipeline_parameters' instead.")
        elif key == 'pipeline_parameters':
            pipeline_params = value
        elif key == 'parent_run_id':
            parent_run_id = value

    return pipeline.submit(experiment_name, pipeline_parameters=pipeline_params,
                           continue_on_step_failure=continue_on_step_failure,
                           regenerate_outputs=regenerate_outputs, parent_run_id=parent_run_id)


class Pipeline(object):
    """
    A Pipeline represents a collection of steps which can be executed as a workflow.

    Use a Pipeline to create and manage workflows that stitch together various machine learning
    phases. Each machine learning phase, such as data preparation and model training, can consist of one or
    more steps in a Pipeline.

    See the following link for an overview on constructing a Pipeline: `https://aka.ms/pl-first-pipeline`

    .. remarks::

        A pipeline is created with a list of steps and a workspace.

        There are a number of Step types which can be used in a Pipeline. Each Step type provides particular
        functionality for various machine learning scenarios.

        The types of Steps which can be used in a Pipeline are:

        *  :class:`azureml.pipeline.steps.adla_step.AdlaStep`
        *  :class:`azureml.train.automl.AutoMLStep`
        *  :class:`azureml.pipeline.steps.azurebatch_step.AzureBatchStep`
        *  :class:`azureml.pipeline.steps.databricks_step.DatabricksStep`
        *  :class:`azureml.pipeline.steps.data_transfer_step.DataTransferStep`
        *  :class:`azureml.pipeline.steps.estimator_step.EstimatorStep`
        *  :class:`azureml.pipeline.steps.hyper_drive_step.HyperDriveStep`
        *  :class:`azureml.pipeline.steps.mpi_step.MpiStep`
        *  :class:`azureml.pipeline.steps.python_script_step.PythonScriptStep`

        Submit a pipeline using :func:`azureml.core.Experiment.submit`. When submit is called,
        a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
        :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow. Use these objects to monitor
        the run execution.

        An example to submit a Pipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline)

        There are a number of optional settings for a Pipeline which can be specified at submission time.
        These include:

        *  continue_on_step_failure: Whether to continue pipeline execution if a step fails, default is False.
        *  regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
            this run, default is False.
        *  pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        *  parent_run_id: You can supply the run id to set the parent run of this pipeline run.

        An example to submit a Pipeline using these settings is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline,
                                             continue_on_step_failure=True,
                                             regenerate_outputs=True,
                                             pipeline_parameters={"param1": "value1"},
                                             parent_run_id="<run_id>")


    :param workspace: The workspace to submit the Pipeline on.
    :type workspace: azureml.core.workspace.Workspace
    :param steps: The list of steps to execute as part of a Pipeline.
    :type steps: builtin.list
    :param description: The description of the Pipeline.
    :type description: str
    :param default_datastore: The default datastore to use for data connections.
    :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
    :param default_source_directory: The default script directory for steps which execute a script.
    :type default_source_directory: str
    :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
    :type resolve_closure: bool
    """

    @experiment_method(submit_function=_submit_pipeline)
    def __init__(self, workspace, steps, description=None,
                 default_datastore=None, default_source_directory=None, resolve_closure=True,
                 _workflow_provider=None, _service_endpoint=None):
        """
        Initialize Pipeline.

        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param steps: The list of steps to execute as part of a Pipeline.
        :type steps: builtin.list
        :param description: The description of the Pipeline.
        :type description: str
        :param default_datastore: The default datastore to use for data connections.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param default_source_directory: The default script directory for steps which execute a script.
        :type default_source_directory: str
        :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
        :type resolve_closure: bool
        :param _workflow_provider: The workflow provider, if None one is created.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint, if None it is determined using the workspace.
        :type _service_endpoint: str
        """
        self._name = description

        self._graph_context = _GraphContext("placeholder", workspace=workspace,
                                            default_source_directory=default_source_directory,
                                            workflow_provider=_workflow_provider,
                                            service_endpoint=_service_endpoint)
        self._graph_builder = _PipelineGraphBuilder(resolve_closure=resolve_closure,
                                                    context=self._graph_context,
                                                    default_datastore=default_datastore)
        if 'aether-dev' in self._graph_context.service_endpoint:
            print('Using dev endpoint:', self._graph_context.service_endpoint)

        self._graph = self._graph_builder.build(self._name, steps, finalize=False)

    def _set_experiment_name(self, name):
        self._graph_context.experiment_name = name
        if self._graph._name is None:
            self._graph._name = name
        if self._name is None:
            self._name = name

    @property
    def graph(self):
        """
        Get the graph associated with the pipeline. Steps and data inputs appear as nodes in the graph.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        return self._graph

    def service_endpoint(self):
        """
        Get the service endpoint associated with the pipeline.

        :return The service endpoint.
        :rtype: str
        """
        return self._graph_context.service_endpoint

    def validate(self):
        """
        Validate a pipeline and identify potential errors, such as unconnected inputs.

        :return: A list of errors in the pipeline.
        :rtype: builtin.list
        """
        return self.graph.validate()

    def _finalize(self, regenerate_outputs=False):
        """
        Finalize the graph.

        :param regenerate_outputs: Whether to regenerate step outputs.
        :type regenerate_outputs: bool

        :return: Dictionary of {node_id, (resource_id, is_new_resource)}
        :rtype: dict
        """
        return self.graph.finalize(regenerate_outputs=regenerate_outputs)

    def submit(self, experiment_name, pipeline_parameters=None, continue_on_step_failure=False,
               regenerate_outputs=False, parent_run_id=None):
        """
        Submit a pipeline run. This is equivalent to using :func:`azureml.core.Experiment.submit`.

        Returns the submitted :class:`azureml.pipeline.core.PipelineRun`. Use this object to monitor and
        view details of the run.

        :param experiment_name: The name of the experiment to submit the pipeline on.
        :type experiment_name: str
        :param pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                    See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Whether to continue pipeline execution if a step fails.
        :type continue_on_step_failure: bool
        :param regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
            this run. If False, this run may reuse results from previous runs and subsequent runs may reuse
            the results of this run.
        :type regenerate_outputs: bool
        :param parent_run_id: You can supply the run id to set the parent run of this pipeline run.
        :type parent_run_id: str

        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        self._set_experiment_name(experiment_name)

        return self.graph.submit(pipeline_parameters=pipeline_parameters,
                                 continue_on_step_failure=continue_on_step_failure,
                                 regenerate_outputs=regenerate_outputs,
                                 parent_run_id=parent_run_id)

    def publish(self, name=None, description=None, version=None, continue_on_step_failure=None):
        """
        Publish a pipeline and make it available for rerunning.

        Once a Pipeline is published, it can be submitted without the Python code which constructed
        the Pipeline. Returns the created :class:`azureml.pipeline.core.PublishedPipeline`.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                         if a step fails, default is false.
        :type continue_on_step_failure: bool

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self.graph._save(name=name, description=description, version=version,
                                continue_on_step_failure=continue_on_step_failure)

    @staticmethod
    def load_yaml(workspace, filename, _workflow_provider=None, _service_endpoint=None):
        r"""
        Load a Pipeline from the specified Yaml file.

        A Yaml file can be used to describe a Pipeline consisting of ModuleSteps.

        .. remarks::

            See below for an example yaml file. The yaml contains a name, default_compute and lists of parameters,
            data references, and steps for the Pipeline. Each step should specify the module, compute and parameter,
            input, and output bindings. Additionally, a step runconfig and arguments can be specified if necessary.

            Sample Yaml file:

            .. code-block:: python

                pipeline:
                    name: SamplePipelineFromYaml
                    parameters:
                        NumIterationsParameter:
                            type: int
                            default: 40
                        DataPathParameter:
                            type: datapath
                            default:
                                datastore: workspaceblobstore
                                path_on_datastore: sample2.txt
                        NodeCountParameter:
                            type: int
                            default: 4
                    data_references:
                        DataReference:
                            datastore: workspaceblobstore
                            path_on_datastore: testfolder/sample.txt
                        Dataset:
                            dataset_name: 'titanic'
                    default_compute: aml-compute
                    steps:
                        PrepareStep:
                            module:
                                name: "TestModule"
                            compute: aml-compute2
                            runconfig: 'D:\.azureml\default_runconfig.yml'
                            arguments:
                            -'--input1'
                            -input:in1
                            -'--input2'
                            -input:in2
                            -'--input3'
                            -input:in3
                            -'--output'
                            -output:output_data
                            -'--param'
                            -parameter:NUM_ITERATIONS
                            parameters:
                                NUM_ITERATIONS:
                                    source: NumIterationsParameter
                            inputs:
                                in1:
                                    source: Dataset
                                    type: mount
                                in2:
                                    source: DataReference
                                in3:
                                    source: DataPathParameter
                            outputs:
                                output_data:
                                    destination: Output1
                                    datastore: workspaceblobstore
                                    type: mount
                        TrainStep:
                            module:
                                name: "TestModule2"
                                version: "2"
                            runconfig: 'D:\.azureml\default_runconfig.yml'
                            arguments:
                            -'--input'
                            -input:train_input
                            -'--output'
                            -output:result
                            -'--param'
                            -parameter:NUM_ITERATIONS
                            parameters:
                                NUM_ITERATIONS: 10
                            runconfig_parameters:
                                NodeCount:
                                    source: NodeCountParameter
                            inputs:
                                train_input:
                                    source: Output1
                                    type: mount
                            outputs:
                                result:
                                    destination: Output2
                                    datastore: workspaceblobstore
                                    type: mount


        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param filename: The Yaml file which describes the Pipeline.
        :type filename: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint, if None it is determined using the workspace.
        :type _service_endpoint: str

        :return: The constructed Pipeline.
        :rtype: azureml.pipeline.core.Pipeline
        """
        import ruamel.yaml.comments
        with open(filename, "r") as input:
            pipeline_yaml = ruamel.yaml.round_trip_load(input)

        if _PIPELINE not in pipeline_yaml:
            raise ValueError('Pipeline Yaml file must have a "pipeline:" section')
        pipeline_section = pipeline_yaml[_PIPELINE]

        name = None
        if _NAME in pipeline_section:
            name = pipeline_section[_NAME]

        pipeline_parameters = Pipeline._get_pipeline_parameters(workspace, pipeline_section)

        default_compute = None
        if _DEFAULT_COMPUTE in pipeline_section:
            default_compute = pipeline_section[_DEFAULT_COMPUTE]

        data_references = Pipeline._get_data_references(workspace, pipeline_section)

        step_objects = []
        pipeline_data_objects = {}

        if _STEPS not in pipeline_section:
            raise ValueError('Pipeline Yaml file must have at least one step defined')

        steps_section = pipeline_section[_STEPS]
        for step_name in steps_section:
            step = steps_section[step_name]
            if _MODULE not in step:
                raise ValueError('Step %s does not contain a "module:" definition' % step_name)
            module_section = step[_MODULE]

            if _ID not in module_section and _NAME not in module_section:
                raise ValueError('Step %s does not contain a module ID or name (one must be specified)' % step_name)
            module_id = module_section.get(_ID, default=None)
            if module_id and not isinstance(module_id, str):
                raise ValueError('Module ID for step %s must be a string' % step_name)
            module_name = module_section.get(_NAME, default=None)
            if module_name and not isinstance(module_name, str):
                raise ValueError('Module name for step %s must be a string' % step_name)

            module_version = module_section.get(_VERSION, default=None)
            if module_version and not isinstance(module_version, str):
                raise ValueError('Module version for step %s must be a string' % step_name)

            module = Module.get(workspace, module_id=module_id, name=module_name,
                                _workflow_provider=_workflow_provider)

            parameter_assignments = {}
            if _PARAMETERS in step:
                parameters_section = step[_PARAMETERS]
                for param_name in parameters_section:
                    current_parameter = parameters_section[param_name]
                    if isinstance(current_parameter, ruamel.yaml.comments.CommentedMap) \
                            and _SOURCE in current_parameter:
                        source_name = current_parameter[_SOURCE]
                        if source_name not in pipeline_parameters:
                            raise ValueError(
                                "Parameter %s for step %s is assigned to source %s, which doesn't exist"
                                % (param_name, step_name, source_name))
                        parameter_assignments[param_name] = pipeline_parameters[current_parameter[_SOURCE]]
                    else:
                        parameter_assignments[param_name] = current_parameter

            runconfig_parameter_assignments = {}
            if _RUNCONFIG_PARAMETERS in step:
                parameters_section = step[_RUNCONFIG_PARAMETERS]
                for param_name in parameters_section:
                    current_parameter = parameters_section[param_name]
                    if isinstance(current_parameter, ruamel.yaml.comments.CommentedMap) \
                            and _SOURCE in current_parameter:
                        source_name = current_parameter[_SOURCE]
                        if source_name not in pipeline_parameters:
                            raise ValueError(
                                "Runconfig Parameter %s for step %s is assigned to source %s, which doesn't exist"
                                % (param_name, step_name, source_name))
                        runconfig_parameter_assignments[param_name] = pipeline_parameters[current_parameter[_SOURCE]]
                    else:
                        runconfig_parameter_assignments[param_name] = current_parameter

            compute = default_compute
            if _COMPUTE in step:
                compute = step[_COMPUTE]

            inputs = {}
            if _INPUTS in step:
                inputs_section = step[_INPUTS]
                for input_name in inputs_section:
                    input = inputs_section[input_name]
                    if _SOURCE not in input:
                        raise ValueError('Input %s for step %s must have a source assignment'
                                         % (input_name, step_name))
                    source_name = input[_SOURCE]
                    input_mode = _MOUNT
                    path_on_compute = None
                    overwrite = None
                    if _TYPE in input:
                        input_mode = input[_TYPE]
                        if input_mode != _MOUNT and input_mode != _DOWNLOAD:
                            raise ValueError('Input type %s for input %s in step %s must be mount or download'
                                             % (input_mode, input_name, step_name))
                    if _PATH_ON_COMPUTE in input:
                        path_on_compute = input[_PATH_ON_COMPUTE]
                    if _OVERWRITE in input:
                        overwrite = input[_OVERWRITE]
                    if source_name in pipeline_parameters and \
                            isinstance(pipeline_parameters[source_name].default_value, DataPath):
                        data_binding = DataPathComputeBinding(mode=input_mode, path_on_compute=path_on_compute,
                                                              overwrite=overwrite)
                        inputs[input_name] = (pipeline_parameters[source_name], data_binding)
                    else:
                        if source_name in data_references:
                            input_source_object = data_references[source_name]
                        else:
                            if source_name not in pipeline_data_objects:
                                pipeline_data_objects[source_name] = PipelineData(name=source_name)
                            input_source_object = pipeline_data_objects[source_name]
                        input_binding = InputPortBinding(name=input_name, bind_object=input_source_object,
                                                         bind_mode=input_mode, path_on_compute=path_on_compute,
                                                         overwrite=overwrite)
                        inputs[input_name] = input_binding

            outputs = {}
            if _OUTPUTS in step:
                outputs_section = step[_OUTPUTS]
                for output_name in outputs_section:
                    output = outputs_section[output_name]
                    if _DESTINATION not in output:
                        raise ValueError('Output %s for step %s must have a destination assignment'
                                         % (output_name, step_name))
                    destination_name = output[_DESTINATION]
                    datastore = None
                    output_mode = _MOUNT
                    path_on_compute = None
                    overwrite = None
                    if _DATASTORE in output:
                        datastore = Datastore(workspace, output[_DATASTORE])
                    if _TYPE in output:
                        output_mode = output[_TYPE]
                        if output_mode != _MOUNT and output_mode != _UPLOAD:
                            raise ValueError('Output type %s for output %s in step %s must be mount or upload'
                                             % (output_mode, output_name, step_name))
                    if _PATH_ON_COMPUTE in output:
                        path_on_compute = output[_PATH_ON_COMPUTE]
                    if _OVERWRITE in output:
                        overwrite = output[_OVERWRITE]
                    if destination_name in pipeline_data_objects:
                        # Already saw this pipeline data from a step input, need to fix the properties
                        pipeline_data_objects[destination_name]._output_name = output_name
                        pipeline_data_objects[destination_name]._datastore = datastore
                        pipeline_data_objects[destination_name]._output_mode = output_mode
                        pipeline_data_objects[destination_name]._output_path_on_compute = path_on_compute
                        pipeline_data_objects[destination_name]._output_overwrite = overwrite
                    else:
                        pipeline_data_objects[destination_name] = PipelineData(
                            name=destination_name, datastore=datastore, output_name=output_name,
                            output_mode=output_mode, output_path_on_compute=path_on_compute,
                            output_overwrite=overwrite)
                    outputs[output_name] = pipeline_data_objects[destination_name]

            arguments = []
            if _ARGUMENTS in step:
                argument_section = step[_ARGUMENTS]
                if isinstance(argument_section, ruamel.yaml.comments.CommentedSeq):
                    argument_section = list(argument_section)
                arguments = argument_section

            resolved_arguments = []
            for arg in arguments:
                if arg.startswith(_ARGUMENT_INPUT):
                    input_name = arg.split(_ARGUMENT_INPUT)[1]
                    if input_name in inputs.keys():
                        resolved_arguments.append(inputs[input_name])
                    else:
                        resolved_arguments.append(arg)
                elif arg.startswith(_ARGUMENT_OUTPUT):
                    output_name = arg.split(_ARGUMENT_OUTPUT)[1]
                    if output_name in outputs.keys():
                        resolved_arguments.append(outputs[output_name])
                    else:
                        resolved_arguments.append(arg)
                elif arg.startswith(_ARGUMENT_PARAMETER):
                    parameter_name = arg.split(_ARGUMENT_PARAMETER)[1]
                    if parameter_name in parameter_assignments.keys():
                        resolved_arguments.append(parameter_name)
                    else:
                        resolved_arguments.append(arg)
                else:
                    resolved_arguments.append(arg)

            runconfig = None
            if _RUNCONFIG in step:
                runconfig_file = step[_RUNCONFIG]
                runconfig = RunConfiguration.load(runconfig_file)

            module_step = ModuleStepBase(module=module, version=module_version,
                                         inputs_map=inputs, outputs_map=outputs,
                                         compute_target=compute, runconfig=runconfig,
                                         runconfig_pipeline_params=runconfig_parameter_assignments,
                                         arguments=resolved_arguments, params=parameter_assignments,
                                         name=step_name, _workflow_provider=_workflow_provider)

            step_objects.append(module_step)

        pipeline = Pipeline(workspace=workspace, steps=step_objects, description=name,
                            _workflow_provider=_workflow_provider, _service_endpoint=_service_endpoint)
        return pipeline

    @staticmethod
    def _get_pipeline_parameters(workspace, pipeline_section):
        pipeline_parameters = {}
        if _PARAMETERS in pipeline_section:
            parameters_section = pipeline_section[_PARAMETERS]
            if parameters_section is not None:
                for parameter_name in parameters_section:
                    current_parameter_section = parameters_section[parameter_name]
                    if _TYPE not in current_parameter_section:
                        raise ValueError('Parameter %s must specify a type of string, int, float, bool, or datapath'
                                         % parameter_name)
                    if _TYPE in current_parameter_section:
                        type = current_parameter_section[_TYPE]
                        default_value = None
                        if type == _STRING:
                            if _DEFAULT in current_parameter_section:
                                default_value = str(current_parameter_section[_DEFAULT])
                        elif type == _INT:
                            if _DEFAULT in current_parameter_section:
                                default_value = int(current_parameter_section[_DEFAULT])
                            else:
                                default_value = 0
                        elif type == _FLOAT:
                            if _DEFAULT in current_parameter_section:
                                default_value = float(current_parameter_section[_DEFAULT])
                            else:
                                default_value = 0.0
                        elif type == _BOOL:
                            if _DEFAULT in current_parameter_section:
                                default_value = bool(current_parameter_section[_DEFAULT])
                            else:
                                default_value = False
                        elif type == _DATAPATH:
                            if _DEFAULT in current_parameter_section:
                                default_section = current_parameter_section[_DEFAULT]
                                if _DATASTORE not in default_section or _PATH_ON_DATASTORE not in default_section:
                                    raise ValueError(
                                        "Default value for datapath parameter %s must specify "
                                        "datastore and path_on_datastore"
                                        % parameter_name)
                                datastore = Datastore(workspace, default_section[_DATASTORE])
                                name = None
                                if _NAME in default_section:
                                    name = default_section[_NAME]
                                default_value = DataPath(datastore=datastore,
                                                         path_on_datastore=default_section[_PATH_ON_DATASTORE],
                                                         name=name)
                        else:
                            raise ValueError("Parameter type %s currently unsupported" % type)
                        pipeline_parameter_object = PipelineParameter(name=parameter_name, default_value=default_value)
                        pipeline_parameters[parameter_name] = pipeline_parameter_object
        return pipeline_parameters

    @staticmethod
    def _get_data_references(workspace, pipeline_section):
        data_references = {}
        if _DATA_REFERENCES in pipeline_section:
            dataref_section = pipeline_section[_DATA_REFERENCES]
            for dataref_name in dataref_section:
                dataref = dataref_section[dataref_name]
                if _DATASTORE in dataref:
                    datastore = Datastore(workspace, dataref[_DATASTORE])
                    if _PATH_ON_DATASTORE in dataref:
                        dataref_object = DataReference(datastore=datastore, data_reference_name=dataref_name,
                                                       path_on_datastore=dataref[_PATH_ON_DATASTORE])
                        data_references[dataref_name] = dataref_object
                    elif _SQL_TABLE in dataref or _SQL_QUERY in dataref or _SQL_STORED_PROCEDURE in dataref or \
                            _SQL_STORED_PROCEDURE_PARAMS in dataref:
                        sql_table = None
                        sql_query = None
                        sql_stored_procedure = None
                        sql_stored_procedure_params = []

                        if _SQL_TABLE in dataref:
                            sql_table = dataref[_SQL_TABLE]
                        if _SQL_QUERY in dataref:
                            sql_query = dataref[_SQL_QUERY]
                        if _SQL_STORED_PROCEDURE in dataref:
                            sql_stored_procedure = dataref[_SQL_STORED_PROCEDURE]

                        if _SQL_STORED_PROCEDURE_PARAMS in dataref:
                            procedure_params_section = dataref[_SQL_STORED_PROCEDURE_PARAMS]
                            for param_name in procedure_params_section:
                                param_section = procedure_params_section[param_name]
                                if _VALUE not in param_section:
                                    raise ValueError('Sql Parameter %s does not contain a "value:" '
                                                     'definition' % param_name)
                                param_value = param_section[_VALUE]
                                param_type = None
                                if _TYPE in param_section:
                                    param_type = StoredProcedureParameterType(param_section[_TYPE])

                                param = StoredProcedureParameter(name=param_name, value=param_value, type=param_type)
                                sql_stored_procedure_params.append(param)

                        sql_dataref = SqlDataReference(datastore=datastore, data_reference_name=dataref_name,
                                                       sql_table=sql_table, sql_query=sql_query,
                                                       sql_stored_procedure=sql_stored_procedure,
                                                       sql_stored_procedure_params=sql_stored_procedure_params)
                        data_references[dataref_name] = sql_dataref
                    else:
                        raise ValueError('Unrecognized data reference type for data reference', dataref_name)
                elif _DATASET_ID in dataref or _DATASET_NAME in dataref:
                    dataset_id = None
                    dataset_name = None

                    if _DATASET_ID in dataref:
                        dataset_id = dataref[_DATASET_ID]
                    if _DATASET_NAME in dataref:
                        dataset_name = dataref[_DATASET_NAME]

                    dataset = Dataset.get(workspace=workspace, name=dataset_name, id=dataset_id)
                    pipeline_dataset = PipelineDataset(dataset=dataset, name=dataref_name)
                    data_references[dataref_name] = pipeline_dataset
                else:
                    raise ValueError('Unrecognized data reference type for data reference', dataref_name)

        return data_references
