# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Windows executable in Azure Batch."""
from azureml.pipeline.core._azurebatch_step_base import _AzureBatchStepBase


class AzureBatchStep(_AzureBatchStepBase):
    r"""
    PipelineStep class for submitting jobs to AzureBatch.

    NOTE: This step does not support upload/download of directories and their contents.

    See example of using this step in notebook https://aka.ms/pl-azbatch

    :param name: Name of the step (mandatory)
    :type name: str
    :param create_pool: Boolean flag to indicate whether create the pool before running the jobs
    :type create_pool: bool
    :param delete_batch_job_after_finish: Boolean flag to indicate whether to delete the job from
                                        Batch account after it's finished
    :type delete_batch_job_after_finish: bool
    :param delete_batch_pool_after_finish: Boolean flag to indicate whether to delete the pool after
                                        the job finishes
    :type delete_batch_pool_after_finish: bool
    :param is_positive_exit_code_failure: Boolean flag to indicate if the job fails if the task exists
                                        with a positive code
    :type is_positive_exit_code_failure: bool
    :param vm_image_urn: If create_pool is true and VM uses VirtualMachineConfiguration.
                         Value format: ``urn:publisher:offer:sku``.
                         Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``
    :type vm_image_urn: str
    :param pool_id: (Mandatory) The Id of the Pool where the job will run
    :type pool_id: str
    :param run_task_as_admin: Boolean flag to indicate if the task should run with Admin privileges
    :type run_task_as_admin: bool
    :param target_compute_nodes: Assumes create_pool is true, indicates how many compute nodes will be added
                                to the pool
    :type target_compute_nodes: int
    :param source_directory: Local folder that contains the module binaries, executable, assemblies etc.
    :type source_directory: str
    :param executable: Name of the command/executable that will be executed as part of the job
    :type executable: str
    :param arguments: Arguments for the command/executable
    :type arguments: str
    :param inputs: List of input port bindings.
        Before the job runs, a folder is created for each input. The files for each input will be copied
        from the storage to the respective folder on the compute node.
        For example, if the input name is *input1*, and the relative path on storage is
        *some/relative/path/that/can/be/really/long/inputfile.txt*, then the file path on the compute
        will be:  *./input1/inputfile.txt*.
        In case the input name is longer than 32 characters, it will be truncated and appended with a unique
        suffix, so the folder name could be created successfully on the compute.
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                    azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings.
        Similar to inputs, before the job runs, a folder is created for each output. The folder name will be
        the same as the output name. The assumption is that the job will have the output into that folder.
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param vm_size: If create_pool is true, indicating Virtual machine size of the compute nodes
    :type vm_size: str
    :param compute_target: BatchCompute compute
    :type compute_target: BatchCompute, str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the module
    :type version: str

    """

    def __init__(self,
                 name,
                 create_pool=False,
                 pool_id=None,
                 delete_batch_job_after_finish=True,
                 delete_batch_pool_after_finish=False,
                 is_positive_exit_code_failure=True,
                 vm_image_urn="urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter",
                 run_task_as_admin=False,
                 target_compute_nodes=1,
                 vm_size="standard_d1_v2",
                 source_directory=None,
                 executable=None,
                 arguments=None,
                 inputs=None,
                 outputs=None,
                 allow_reuse=True,
                 compute_target=None,
                 version=None):
        r"""
        Pipelinestep class for submitting jobs to AzureBatch.

        :param name: Name of the step (mandatory)
        :type name: str
        :param create_pool: Boolean flag to indicate whether create the pool before running the jobs
        :type create_pool: bool
        :param delete_batch_job_after_finish: Boolean flag to indicate whether to delete the job from
                                            Batch account after it's finished
        :type delete_batch_job_after_finish: bool
        :param delete_batch_pool_after_finish: Boolean flag to indicate whether to delete the pool after
                                            the job finishes
        :type delete_batch_pool_after_finish: bool
        :param is_positive_exit_code_failure: Boolean flag to indicate if the job fails if the task exists
                                            with a positive code
        :type is_positive_exit_code_failure: bool
        :param vm_image_urn: If create_pool is true and VM uses VirtualMachineConfiguration.
                             Value format: ``urn:publisher:offer:sku``.
                             Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``
        :type vm_image_urn: str
        :param pool_id: (Mandatory) The Id of the Pool where the job will run
        :type pool_id: str
        :param run_task_as_admin: Boolean flag to indicate if the task should run with Admin privileges
        :type run_task_as_admin: bool
        :param target_compute_nodes: Assumes create_pool is true, indicates how many compute nodes will be added
                                    to the pool
        :type target_compute_nodes: int
        :param source_directory: Local folder that contains the module binaries, executable, assemblies etc.
        :type source_directory: str
        :param executable: Name of the command/executable that will be executed as part of the job
        :type executable: str
        :param arguments: Arguments for the command/executable
        :type arguments: list
        :param inputs: List of input port bindings.
            Before the job runs, a folder is created for each input. The files for each input will be copied
            from the storage to the respective folder on the compute node.
            For example, if the input name is *input1*, and the relative path on storage is
            *some/relative/path/that/can/be/really/long/inputfile.txt*, then the file path on the compute
            will be:  *./input1/inputfile.txt*.
            In case the input name is longer than 32 characters, it will be truncated and appended with a unique
            suffix, so the folder name could be created successfully on the compute.
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                        azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                        azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings.
            Similar to inputs, before the job runs, a folder is created for each output. The folder name will be
            the same as the output name. The assumption is that the job will have the output into that folder.
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param vm_size: If create_pool is true, indicating Virtual machine size of the compute nodes
        :type vm_size: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the module
        :type version: str

        """
        super(AzureBatchStep, self).__init__(
            name=name, create_pool=create_pool, pool_id=pool_id,
            delete_batch_job_after_finish=delete_batch_job_after_finish,
            delete_batch_pool_after_finish=delete_batch_pool_after_finish,
            is_positive_exit_code_failure=is_positive_exit_code_failure,
            vm_image_urn=vm_image_urn,
            run_task_as_admin=run_task_as_admin,
            target_compute_nodes=target_compute_nodes,
            vm_size=vm_size,
            source_directory=source_directory,
            executable=executable,
            arguments=arguments,
            inputs=inputs,
            outputs=outputs,
            allow_reuse=allow_reuse,
            compute_target=compute_target,
            version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the AzureBatch step and adds it to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(AzureBatchStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                       context=context)
