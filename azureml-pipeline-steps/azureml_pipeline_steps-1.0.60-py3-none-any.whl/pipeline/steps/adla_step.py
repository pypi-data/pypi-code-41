# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""To add a step to run U-SQL script using Azure Data Lake Analytics."""
from azureml.pipeline.core._adla_step_base import _AdlaStepBase


class AdlaStep(_AdlaStepBase):
    """Adds a step to run U-SQL script using Azure Data Lake Analytics.

    See example of using this step in notebook https://aka.ms/pl-adla

    .. remarks::

        You can use `@@name@@` syntax in your script to refer to inputs, outputs, and params.

        * if `name` is the name of an input or output port binding, any occurrences of `@@name@@` in the script
          are replaced with actual data path of corresponding port binding.
        * if `name` matches any key in `params` dict, any occurrences of `@@name@@` will be replaced with
          corresponding value in dict.

    :param script_name: name of usql script (relative to source_directory)
    :type script_name: str
    :param name: Name of the step.  If unspecified, script_name will be used
    :type name: str
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param params: Dictionary of name-value pairs
    :type params: dict
    :param degree_of_parallelism: the degree of parallelism to use for this job
    :type degree_of_parallelism: int
    :param priority: the priority value to use for the current job
    :type priority: int
    :param runtime_version: the runtime version of the Data Lake Analytics engine
    :type runtime_version: str
    :param compute_target: the ADLA compute to use for this job
    :type compute_target: azureml.core.compute.AdlaCompute, str
    :param source_directory: folder that contains the script, assemblies etc.
    :type source_directory: str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None, inputs=None, outputs=None, params=None, degree_of_parallelism=None,
                 priority=None, runtime_version=None, compute_target=None, source_directory=None, allow_reuse=True,
                 version=None, hash_paths=None):
        """
        Initialize AdlaStep.

        :param script_name: name of usql script (relative to source_directory)
        :type script_name: str
        :param name: Name of the step.  If unspecified, script_name will be used
        :type name: str
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param params: Dictionary of name-value pairs
        :type params: dict
        :param degree_of_parallelism: the degree of parallelism to use for this job
        :type degree_of_parallelism: int
        :param priority: the priority value to use for the current job
        :type priority: int
        :param runtime_version: the runtime version of the Data Lake Analytics engine
        :type runtime_version: str
        :param compute_target: the ADLA compute to use for this job
        :type compute_target: azureml.core.compute.AdlaCompute, str
        :param source_directory: folder that contains the script, assemblies etc.
        :type source_directory: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
        :type hash_paths: list
        """
        super(AdlaStep, self).__init__(
            script_name=script_name, name=name, inputs=inputs, outputs=outputs,
            params=params, degree_of_parallelism=degree_of_parallelism, priority=priority,
            runtime_version=runtime_version, compute_target=compute_target,
            source_directory=source_directory, allow_reuse=allow_reuse, version=version, hash_paths=hash_paths)

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
        return super(AdlaStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
