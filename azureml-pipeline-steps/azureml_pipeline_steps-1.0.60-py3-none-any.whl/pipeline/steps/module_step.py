# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to use an existing version of a Module."""
from azureml.pipeline.core.module_step_base import ModuleStepBase


class ModuleStep(ModuleStepBase):
    """Adds a step that uses a specific module.

    A ModuleStep is a node in pipeline that uses an existing Module, and specifically, one of its versions.
    In order to define which ModuleVersion would eventually be used in the submitted pipeline, the user can define
    one of the following when creating the ModuleStep:
    -   ModuleVersion object
    -   Module object and a version value
    -   Only Module without a version value, in this case the resolution is to use may vary across submissions.

    The user also needs to define the mapping between the step's inputs and outputs to the ModuleVersion's inputs
    and outputs.

    :param module: Module of the step
    :type module: azureml.pipeline.core.Module
    :param version: version of the module
    :type version: str
    :param module_version: ModuleVersion of the step. Either Module of ModuleVersion must be provided
    :type module_version: azureml.pipeline.core.ModuleVersion
    :param inputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
    :type inputs_map: {str: azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset}
    :param outputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
    :type outputs_map: {str: azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset}
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param arguments: Command line arguments for the python script file. The arguments will be delivered
                      to compute via arguments in RunConfiguration.
                      For more details how to handle arguments such as special symbols, please refer
                      arguments in :class:`azureml.core.RunConfiguration`
    :type arguments: [str]
    :param params: Dictionary of name-value pairs
    :type params: {str: str}
    """

    def __init__(self, module=None, version=None, module_version=None,
                 inputs_map=None, outputs_map=None,
                 compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, arguments=None, params=None, name=None,
                 _workflow_provider=None):
        """
        Initialize ModuleStep.

        :param module: Module of the step
        :type module: azureml.pipeline.core.Module
        :param version: version of the module
        :type version: str
        :param module_version: ModuleVersion of the step. Either Module of ModuleVersion must be provided
        :type module_version: azureml.pipeline.core.ModuleVersion
        :param inputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
        :type inputs_map: {str:
                      azureml.pipeline.core.graph.InputPortBinding,azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset}
        :param outputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
        :type outputs_map: {str:
                      azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset}
        :param compute_target: Compute target to use.  If unspecified, the target from the runconfig will be used.
            compute_target may be a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteTarget type is 'VirtualMachine')
        :type compute_target: DsvmCompute, AmlCompute, RemoteTarget, HDIClusterTarget, str, tuple
        :param runconfig: The RunConfiguration to use, optional. A RunConfiguration can be used to specify additional
                      requirements for the run, such as conda dependencies and a docker image.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                        name of the runconfig property and PipelineParameter for that property
        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param arguments: Command line arguments for the python script file. The arguments will be delivered
                          to compute via arguments in RunConfiguration.
                          For more details how to handle arguments such as special symbols, please refer
                          arguments in :class:`azureml.core.RunConfiguration`
        :type arguments: [str]
        :param params: Dictionary of name-value pairs
        :type params: {str: str}
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        """
        super(ModuleStep, self).__init__(module=module, version=version, module_version=module_version,
                                         inputs_map=inputs_map, outputs_map=outputs_map,
                                         compute_target=compute_target, runconfig=runconfig,
                                         runconfig_pipeline_params=runconfig_pipeline_params, arguments=arguments,
                                         params=params, name=name, _workflow_provider=_workflow_provider)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: context
        :type context: _GraphContext

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(ModuleStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
