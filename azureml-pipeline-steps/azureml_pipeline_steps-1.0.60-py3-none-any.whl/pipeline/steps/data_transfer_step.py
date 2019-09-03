# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To transfer data between various storages.

Supports Azure Blob, Azure Data Lake Store, Azure SQL database and Azure database for PostgreSQL.
"""
from azureml.pipeline.core._data_transfer_step_base import _DataTransferStepBase


class DataTransferStep(_DataTransferStepBase):
    """Add a step to transfer data between various storage options.

     Supports Azure Blob, Azure Data Lake store, Azure SQL database and Azure database for PostgreSQL.

     See example of using this step in notebook https://aka.ms/pl-data-trans

    .. remarks::

        To establish data dependency between steps, use
        :func:`azureml.pipeline.steps.data_transfer_step.DataTransferStep.get_output` method to get a
        :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
        transfer step and can be used as input for later steps in the pipeline.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)

            # Use output of data_transfer_step as input of another step in pipeline
            # This will make training_step wait for data_transfer_step to complete
            training_input = data_transfer_step.get_output()
            training_step = PythonScriptStep(script_name="train.py",
                                    arguments=["--model", training_input],
                                    inputs=[training_input],
                                    compute_target=aml_compute,
                                    source_directory=source_directory)

        To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
        `get_output()` call with :func:`azureml.pipeline.core.PipelineData.as_input` or
        :func:`azureml.pipeline.core.PipelineData.as_mount` helper methods.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)

            training_input = data_transfer_step.get_output().as_input("my_input_name")


    :param name: Name of the step
    :type name: str
    :param source_data_reference: Input connection that serves as source of data transfer operation
    :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData, azureml.core.Dataset,
                  azureml.data.dataset_definition.DatasetDefinition, azureml.pipeline.core.PipelineDataset]
    :param destination_data_reference: Input connection that serves as destination of data transfer operation
    :type destination_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                                           azureml.data.data_reference.DataReference]
    :param compute_target: Azure Data Factory to use for transferring data
    :type compute_target: DataFactoryCompute, str
    :param source_reference_type: An optional string specifying the type of source_data_reference. Possible values
                                  include: 'file', 'directory'. When not specified, we use the type of existing path.
                                  Use it to differentiate between a file and directory of the same name.
    :type source_reference_type: str
    :param destination_reference_type: An optional string specifying the type of destination_data_reference. Possible
                                       values include: 'file', 'directory'. When not specified, we use the type of
                                       existing path, source reference, or 'directory', in that order.
    :type destination_reference_type: str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
        run of this step is reused. When reusing the step, instead of transferring data again, the results from
        the previous run are immediately made available to any subsequent steps.
    :type allow_reuse: bool
    """

    def __init__(self, name, source_data_reference=None, destination_data_reference=None, compute_target=None,
                 source_reference_type=None, destination_reference_type=None, allow_reuse=True):
        """
        Initialize DataTransferStep.

        :param name: Name of the step
        :type name: str
        :param source_data_reference: Input connection that serves as source of data transfer operation
        :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData, azureml.core.Dataset,
                    azureml.data.dataset_definition.DatasetDefinition, azureml.pipeline.core.PipelineDataset]
        :param destination_data_reference: Input connection that serves as destination of data transfer operation
        :type destination_data_reference:
                    list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference]
        :param compute_target: Azure Data Factory to use for transferring data
        :type compute_target: DataFactoryCompute, str
        :param source_reference_type: An optional string specifying the type of source_data_reference. Possible values
                                      include: 'file', 'directory'. When not specified, we use the type of existing
                                      path. Use it to differentiate between a file and directory of the same name.
        :type source_reference_type: str
        :param destination_reference_type: An optional string specifying the type of destination_data_reference.
                                           Possible values include: 'file', 'directory'. When not specified, we use
                                           the type of existing path, source reference, or 'directory', in that order.
        :type destination_reference_type: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
            run of this step is reused. When reusing the step, instead of transferring data again, the results from
            the previous run are immediately made available to any subsequent steps.
        :type allow_reuse: bool
        """
        super(DataTransferStep, self).__init__(
            name=name, source_data_reference=source_data_reference,
            destination_data_reference=destination_data_reference, compute_target=compute_target,
            source_reference_type=source_reference_type, destination_reference_type=destination_reference_type,
            allow_reuse=allow_reuse)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this DataTransfer step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(DataTransferStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                         context=context)

    def get_output(self):
        """
        Get the output of the step as PipelineData.

        .. remarks::

            To establish data dependency between steps, use :func:`azureml.pipeline.steps.DataTransferStep.get_output`
            method to get a :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
            transfer step and can be used as input for later steps in the pipeline.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                # Use output of data_transfer_step as input of another step in pipeline
                # This will make training_step wait for data_transfer_step to complete
                training_input = data_transfer_step.get_output()
                training_step = PythonScriptStep(script_name="train.py",
                                        arguments=["--model", training_input],
                                        inputs=[training_input],
                                        compute_target=aml_compute,
                                        source_directory=source_directory)

            To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
            `get_output()` call with :func:`azureml.pipeline.core.PipelineData.as_input` or
            :func:`azureml.pipeline.core.PipelineData.as_mount` helper methods.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                training_input = data_transfer_step.get_output().as_input("my_input_name")

        :return: The output of the step.
        :rtype: azureml.pipeline.core.builder.PipelineData
        """
        return super(DataTransferStep, self).get_output()
