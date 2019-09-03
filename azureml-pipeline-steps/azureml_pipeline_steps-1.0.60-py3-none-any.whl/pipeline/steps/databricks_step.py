# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Databricks notebook or a python script on DBFS."""
from azureml.pipeline.core._databricks_step_base import _DatabricksStepBase


class DatabricksStep(_DatabricksStepBase):
    """Add a DataBricks notebook, python script or JAR as a node.

    See example of using this step in notebook https://aka.ms/pl-databricks

    :param name: Name of the step
    :type name: str
    :param inputs: List of input connections for data consumed by this step. Fetch this inside the notebook
                    using dbutils.widgets.get("input_name"). Can be DataReference or PipelineData. DataReference
                    represents an existing piece of data on a datastore. Essentially this is a path on a
                    datastore. DatabricksStep supports datastores that encapsulates DBFS, Azure blob or ADLS v1.
                    PipelineData represents intermediate data produced by another step in a pipeline.
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                       azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                       azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                       azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port definitions for outputs produced by this step. Fetch this inside the
                    notebook using dbutils.widgets.get("output_name"). Should be PipelineData.
    :type outputs: list[azureml.pipeline.core.graph.OutputPortBinding, azureml.pipeline.core.builder.PipelineData]
    :param existing_cluster_id: Cluster ID of an existing interactive cluster on the Databricks workspace.
        If you are passing this parameter, you cannot pass any of the following parameters which are used to
        create a new cluster:
        -   spark_version
        -   node_type
        -   instance_pool_id
        -   num_workers
        -   min_workers
        -   max_workers
        -   spark_env_variables
        -   spark_conf

        Note: For creating a new job cluster, you will need to pass the above parameters. You can pass
        these parameters directly or you can pass them as part of the RunConfiguration object using the
        runconfig parameter. However, you can’t pass the parameters via runconfig and directly at the same time
        as that will lead to ambiguity, and hence, DatabricksStep will report an error.
    :type existing_cluster_id: str
    :param spark_version: The version of spark for the Databricks run cluster. Example: "4.0.x-scala2.11"
    :type spark_version: str
    :param node_type: The Azure VM node types for the Databricks run cluster. Example: "Standard_D3_v2"
    :type node_type: str
    :param instance_pool_id: The instance pool Id to which the cluster needs to be attached to.
    :type instance_pool_id: str
    :param num_workers: Specifies a static number of workers for the Databricks run cluster.
                        Exactly one of num_workers or min_workers and max_workers is required
    :type num_workers: int
    :param min_workers: Specifies a min number of workers to use for auto-scaling the Databricks run cluster
    :type min_workers: int
    :param max_workers: Specifies a max number of workers to use for auto-scaling the Databricks run cluster
    :type max_workers: int
    :param spark_env_variables: The spark environment variables for the Databricks run cluster
    :type spark_env_variables: dict
    :param spark_conf: The spark configuration for the Databricks run cluster
    :type spark_conf: dict
    :param init_scripts: DBFS paths to init scripts for the new cluster
    :type init_scripts: [str]
    :param cluster_log_dbfs_path: DBFS paths to where clusters logs need to be delivered
    :type cluster_log_dbfs_path: str

    :param notebook_path: The path to the notebook in the Databricks instance. This class allows four ways of
                          specifying the code that you wish to execute on the Databricks cluster.
                          1.	If you want to execute a notebook that is present in the Databricks workspace:
                          notebook_path=notebook_path,
                          notebook_params={'myparam': 'testparam'},
                          2.	If you want to execute a Python script that is present in DBFS:
                          python_script_path=python_script_dbfs_path,
                          python_script_params={'arg1', 'arg2'},
                          3.	If you want to execute a JAR that is present in DBFS:
                          main_class_name=main_jar_class_name,
                          jar_params={'arg1', 'arg2'},
                          jar_libraries=[JarLibrary(jar_library_dbfs_path)],
                          4.	If you want to execute a Python script that is present on your local machine:
                          python_script_name=python_script_name,
                          source_directory=source_directory,
    :type notebook_path: str
    :param notebook_params: Dictionary of parameters to be passed to notebook. `notebook_params` parameter
        are available as widgets. You can fetch the values from these widgets inside your notebook
        using `dbutils.widgets.get("myparam")`.
    :type notebook_params: dict{str:str, str:PipelineParameter}
    :param python_script_path: The path to the python script in the DBFS or S3.
    :type python_script_path: str
    :param python_script_params: Parameters for the python script.
    :type python_script_params: list[str, PipelineParameter]
    :param main_class_name: The name of the entry point in a JAR module.
    :type main_class_name: str
    :param jar_params: Parameters for the JAR module.
    :type jar_params: list[str, PipelineParameter]
    :param python_script_name: Name of a python script (relative to source_directory). If the script takes inputs
        and outputs, those will be passed to the script as parameters.

        If you specify a DataReference object as input with `data_reference_name="input1` and a
        PipelineData object as output with `name=output1`, then the inputs and outputs will be passed to the script
        as parameters. This is how they will look like and you will need to parse the arguments
        in your script to access the paths of each input and output:
        `"—input1","wasbs://test@storagename.blob.core.windows.net/test","—output1",
        "wasbs://test@storagename.blob.core.windows.net/b3e26de1-87a4-494d-a20f-1988d22b81a2/output1"`

        In addition, the following parameters will be available within the script:
        -   AZUREML_RUN_TOKEN: The AML token for authenticating with Azure Machine Learning.
        -   AZUREML_RUN_TOKEN_EXPIRY: The AML token expiry time.
        -   AZUREML_RUN_ID: Azure Machine Learning Run ID for this run.
        -   AZUREML_ARM_SUBSCRIPTION: Azure subscription for your AML workspace.
        -   AZUREML_ARM_RESOURCEGROUP: Azure resource group for your Azure Machine Learning workspace.
        -   AZUREML_ARM_WORKSPACE_NAME: Name of your Azure Machine Learning workspace.
        -   AZUREML_ARM_PROJECT_NAME: Name of your Azure Machine Learning experiment.
        -   AZUREML_SCRIPT_DIRECTORY_NAME: Directory path structure in DBFS where source_directory has been copied.
        -   AZUREML_SERVICE_ENDPOINT: The endpoint URL for AML services.

        When you are executing a python script from your local machine on Databricks using
        AZUREML_SCRIPT_DIRECTORY_NAME_ARG_VARIABLE DatabricksStep your source_directory is copied over to DBFS
        and the directory structure path on DBFS is passed as a parameter to your script when it begins execution.
        This parameter is labelled as --AZUREML_SCRIPT_DIRECTORY_NAME. You need to prefix it with the
        string "dbfs:/" or "/dbfs/" to access the directory in DBFS.
    :type python_script_name: str
    :param source_directory: Folder that contains the script and other files
    :type source_directory: str
    :param hash_paths: List of paths to hash when checking for changes to the contents of source_directory.  If
        there are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
        contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
        (DEPRECATED), no longer needed.
    :type hash_paths: [str]
    :param run_name: The name in Databricks for this run
    :type run_name: str
    :param timeout_seconds: Timeout for the Databricks run
    :type timeout_seconds: int
    :param runconfig: Runconfig to use
        Note: You can pass the following libraries (as many as you like) as dependencies to your job
        using the following parameters: maven_libraries, pypi_libraries, egg_libraries, jar_libraries,
        or rcran_libraries. You can pass these parameters directly or as part of the RunConfiguration
        object using the runconfig parameter, but you cannot do both at the same time.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param maven_libraries: Maven libraries for the Databricks run
    :type maven_libraries: list[azureml.core.runconfig.MavenLibrary]
    :param pypi_libraries: PyPi libraries for the Databricks run
    :type pypi_libraries: list[azureml.core.runconfig.PyPiLibrary]
    :param egg_libraries: egg libraries for the Databricks run
    :type egg_libraries: list[azureml.core.runconfig.EggLibrary]
    :param jar_libraries: jar libraries for the Databricks run
    :type jar_libraries: list[azureml.core.runconfig.JarLibrary]
    :param rcran_libraries: rcran libraries for the Databricks run
    :type rcran_libraries: list[azureml.core.runconfig.RCranLibrary]
    :param compute_target: Azure Databricks compute. Before you can use DatabricksStep to execute your scripts
        or notebooks on an Azure Databricks workspace, you need to add the Azure Databricks workspace as a
        compute target to your Azure Machine Learning workspace.
    :type compute_target: str, azureml.core.compute.DatabricksCompute
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    """

    def __init__(self, name, inputs=None, outputs=None, existing_cluster_id=None, spark_version=None,
                 node_type=None, instance_pool_id=None, num_workers=None, min_workers=None, max_workers=None,
                 spark_env_variables=None, spark_conf=None, init_scripts=None, cluster_log_dbfs_path=None,
                 notebook_path=None, notebook_params=None, python_script_path=None, python_script_params=None,
                 main_class_name=None, jar_params=None, python_script_name=None, source_directory=None,
                 hash_paths=None, run_name=None, timeout_seconds=None, runconfig=None, maven_libraries=None,
                 pypi_libraries=None, egg_libraries=None, jar_libraries=None, rcran_libraries=None,
                 compute_target=None, allow_reuse=True, version=None):
        """Add a DataBricks notebook, python script or JAR as a node.

        See example of using this step in notebook https://aka.ms/pl-databricks

        :param name: Name of the step
        :type name: str
        :param inputs: List of input connections for data consumed by this step. Fetch this inside the notebook
                        using dbutils.widgets.get("input_name"). Can be DataReference or PipelineData. DataReference
                        represents an existing piece of data on a datastore. Essentially this is a path on a
                        datastore. DatabricksStep supports datastores that encapsulates DBFS, Azure blob or ADLS v1.
                        PipelineData represents intermediate data produced by another step in a pipeline.
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                           azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                           azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                           azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port definitions for outputs produced by this step. Fetch this inside the
                        notebook using dbutils.widgets.get("output_name"). Should be PipelineData.
        :type outputs: list[azureml.pipeline.core.graph.OutputPortBinding, azureml.pipeline.core.builder.PipelineData]
        :param existing_cluster_id: Cluster ID of an existing interactive cluster on the Databricks workspace.
            If you are passing this parameter, you cannot pass any of the following parameters which are used to
            create a new cluster:
            -   spark_version
            -   node_type
            -   instance_pool_id
            -   num_workers
            -   min_workers
            -   max_workers
            -   spark_env_variables
            -   spark_conf

            Note: For creating a new job cluster, you will need to pass the above parameters. You can pass
            these parameters directly or you can pass them as part of the RunConfiguration object using the
            runconfig parameter. However, you can’t pass the parameters via runconfig and directly at the same time
            as that will lead to ambiguity, and hence, DatabricksStep will report an error.
        :type existing_cluster_id: str
        :param spark_version: The version of spark for the Databricks run cluster. Example: "4.0.x-scala2.11"
        :type spark_version: str
        :param node_type: The Azure VM node types for the Databricks run cluster. Example: "Standard_D3_v2"
        :type node_type: str
        :param instance_pool_id: The instance pool Id to which the cluster needs to be attached to.
        :type instance_pool_id: str
        :param num_workers: Specifies a static number of workers for the Databricks run cluster.
                            Exactly one of num_workers or min_workers and max_workers is required
        :type num_workers: int
        :param min_workers: Specifies a min number of workers to use for auto-scaling the Databricks run cluster
        :type min_workers: int
        :param max_workers: Specifies a max number of workers to use for auto-scaling the Databricks run cluster
        :type max_workers: int
        :param spark_env_variables: The spark environment variables for the Databricks run cluster
        :type spark_env_variables: dict
        :param spark_conf: The spark configuration for the Databricks run cluster
        :type spark_conf: dict
        :param init_scripts: DBFS paths to init scripts for the new cluster
        :type init_scripts: [str]
        :param cluster_log_dbfs_path: DBFS paths to where clusters logs need to be delivered
        :type cluster_log_dbfs_path: str

        :param notebook_path: The path to the notebook in the Databricks instance. This class allows four ways of
                              specifying the code that you wish to execute on the Databricks cluster.
                              1.	If you want to execute a notebook that is present in the Databricks workspace:
                              notebook_path=notebook_path,
                              notebook_params={'myparam': 'testparam'},
                              2.	If you want to execute a Python script that is present in DBFS:
                              python_script_path=python_script_dbfs_path,
                              python_script_params={'arg1', 'arg2'},
                              3.	If you want to execute a JAR that is present in DBFS:
                              main_class_name=main_jar_class_name,
                              jar_params={'arg1', 'arg2'},
                              jar_libraries=[JarLibrary(jar_library_dbfs_path)],
                              4.	If you want to execute a Python script that is present on your local machine:
                              python_script_name=python_script_name,
                              source_directory=source_directory,
        :type notebook_path: str
        :param notebook_params: Dictionary of parameters to be passed to notebook. `notebook_params` parameter
            are available as widgets. You can fetch the values from these widgets inside your notebook
            using `dbutils.widgets.get("myparam")`.
        :type notebook_params: dict{str:str, str:PipelineParameter}
        :param python_script_path: The path to the python script in the DBFS or S3.
        :type python_script_path: str
        :param python_script_params: Parameters for the python script.
        :type python_script_params: list[str, PipelineParameter]
        :param main_class_name: The name of the entry point in a JAR module.
        :type main_class_name: str
        :param jar_params: Parameters for the JAR module.
        :type jar_params: list[str, PipelineParameter]
        :param python_script_name: Name of a python script (relative to source_directory). If the script takes inputs
            and outputs, those will be passed to the script as parameters.

            If you specify a DataReference object as input with `data_reference_name="input1` and a
            PipelineData object as output with `name=output1`, then the inputs and outputs will be passed to the script
            as parameters. This is how they will look like and you will need to parse the arguments
            in your script to access the paths of each input and output:
            `"—input1","wasbs://test@storagename.blob.core.windows.net/test","—output1",
            "wasbs://test@storagename.blob.core.windows.net/b3e26de1-87a4-494d-a20f-1988d22b81a2/output1"`

            In addition, the following parameters will be available within the script:
            -   AZUREML_RUN_TOKEN: The AML token for authenticating with Azure Machine Learning.
            -   AZUREML_RUN_TOKEN_EXPIRY: The AML token expiry time.
            -   AZUREML_RUN_ID: Azure Machine Learning Run ID for this run.
            -   AZUREML_ARM_SUBSCRIPTION: Azure subscription for your AML workspace.
            -   AZUREML_ARM_RESOURCEGROUP: Azure resource group for your Azure Machine Learning workspace.
            -   AZUREML_ARM_WORKSPACE_NAME: Name of your Azure Machine Learning workspace.
            -   AZUREML_ARM_PROJECT_NAME: Name of your Azure Machine Learning experiment.
            -   AZUREML_SCRIPT_DIRECTORY_NAME: Directory path structure in DBFS where source_directory has been copied.
            -   AZUREML_SERVICE_ENDPOINT: The endpoint URL for AML services.

            When you are executing a python script from your local machine on Databricks using
            AZUREML_SCRIPT_DIRECTORY_NAME_ARG_VARIABLE DatabricksStep your source_directory is copied over to DBFS
            and the directory structure path on DBFS is passed as a parameter to your script when it begins execution.
            This parameter is labelled as --AZUREML_SCRIPT_DIRECTORY_NAME. You need to prefix it with the
            string "dbfs:/" or "/dbfs/" to access the directory in DBFS.
        :type python_script_name: str
        :param source_directory: Folder that contains the script and other files
        :type source_directory: str
        :param hash_paths: List of paths to hash when checking for changes to the contents of source_directory.  If
            there are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
        :type hash_paths: [str]
        :param run_name: The name in Databricks for this run
        :type run_name: str
        :param timeout_seconds: Timeout for the Databricks run
        :type timeout_seconds: int
        :param runconfig: Runconfig to use
            Note: You can pass the following libraries (as many as you like) as dependencies to your job
            using the following parameters: maven_libraries, pypi_libraries, egg_libraries, jar_libraries,
            or rcran_libraries. You can pass these parameters directly or as part of the RunConfiguration
            object using the runconfig parameter, but you cannot do both at the same time.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param maven_libraries: Maven libraries for the Databricks run
        :type maven_libraries: list[azureml.core.runconfig.MavenLibrary]
        :param pypi_libraries: PyPi libraries for the Databricks run
        :type pypi_libraries: list[azureml.core.runconfig.PyPiLibrary]
        :param egg_libraries: egg libraries for the Databricks run
        :type egg_libraries: list[azureml.core.runconfig.EggLibrary]
        :param jar_libraries: jar libraries for the Databricks run
        :type jar_libraries: list[azureml.core.runconfig.JarLibrary]
        :param rcran_libraries: rcran libraries for the Databricks run
        :type rcran_libraries: list[azureml.core.runconfig.RCranLibrary]
        :param compute_target: Azure Databricks compute. Before you can use DatabricksStep to execute your scripts
            or notebooks on an Azure Databricks workspace, you need to add the Azure Databricks workspace as a
            compute target to your Azure Machine Learning workspace.
        :type compute_target: str, azureml.core.compute.DatabricksCompute
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        """
        super(DatabricksStep, self).__init__(
            name=name, inputs=inputs, outputs=outputs, existing_cluster_id=existing_cluster_id,
            spark_version=spark_version,
            node_type=node_type, instance_pool_id=instance_pool_id, num_workers=num_workers, min_workers=min_workers,
            max_workers=max_workers, spark_env_variables=spark_env_variables, spark_conf=spark_conf,
            init_scripts=init_scripts, cluster_log_dbfs_path=cluster_log_dbfs_path, notebook_path=notebook_path,
            notebook_params=notebook_params, python_script_path=python_script_path,
            python_script_params=python_script_params, main_class_name=main_class_name, jar_params=jar_params,
            python_script_name=python_script_name, source_directory=source_directory, hash_paths=hash_paths,
            run_name=run_name, timeout_seconds=timeout_seconds, runconfig=runconfig, maven_libraries=maven_libraries,
            pypi_libraries=pypi_libraries, egg_libraries=egg_libraries, jar_libraries=jar_libraries,
            rcran_libraries=rcran_libraries, compute_target=compute_target, allow_reuse=allow_reuse, version=version)

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        result = "DatabricksStep_{0}".format(self.name)
        return result

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        return self.__str__()

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this Databricks step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(DatabricksStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                       context=context)
