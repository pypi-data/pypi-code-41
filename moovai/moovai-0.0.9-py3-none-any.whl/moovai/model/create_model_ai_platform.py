import sys
sys.path.append(".")
sys.path.append("..")
from google.cloud import error_reporting
from googleapiclient import discovery


def create_model(model_name, project_id, region=None):
    """
    Creates a model instance on Google's AI platform
    :param model_name: STRING. REQUIRED. name of model to create
    :param project_id: STRING. REQUIRED. project ID where model is to be created
    :param region: STRING. OPTIONAL. Defaults to us-east1
    :return: None. Creates model.
    """
    project = f"projects/{project_id}"
    ml = discovery.build('ml', 'v1')
    if region is None:
        region = 'us-east1'
    request_dict = {
        'name': f"{model_name}",
        'regions': [
            f"{region}"
        ]
    }

    # define request to call projects.models.create
    request = ml.projects().models().create(
        parent=project,
        body=request_dict
    )

    # Make API request call

    try:
        response = request.execute()
        print(response)
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()


def create_version(model_name, version_name, project_id, deployment_uri):
    """
    Create model version on AI platform.
    :param model_name: STRING. REQUIRED. name of model
    :param version_name: STRING. REQUIRED. version name (should be kept simple eg: v1) Must be unique within the model it is created in
    :param project_id: STRING. REQUIRED. project id
    :param deployment_uri: STRING. REQUIRED. GCS URI to folder containing your saved_model.pb to use for predictions.
    :return: None. Model version created on AI platform.
    """
    project = f"projects/{project_id}"
    model_id = f"{project}/models/{model_name}"
    ml = discovery.build('ml', 'v1')

    request_dict = {
        'name': version_name,
        'deploymentUri': f"{deployment_uri}",
        'runtimeVersion': '1.9',
        'framework': 'TENSORFLOW',
        'pythonVersion': '3.5'
    }

    request = ml.projects().models().versions().create(
        parent=model_id,
        body=request_dict
    )

    #Make API request call

    try:
        response = request.execute()
        print(response)
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()


def create_model_version(model_name, model_version, project_id, deployment_uri):
    """
    Creates model instance on AI platform, then creates a model version for the newly created model
    :param model_name: STRING. REQUIRED. Name of model to be created.
    :param model_version: STRING. REQUIRED. Name of version to be created within model. must be unique
    :param project_id: STRING. REQUIRED. project ID where model and version will be created
    :param deployment_uri: STRING. REQUIRED. GCS URI path to folder containing saved_model.pb file.
    :return: None. Creates model and model version on AI platform in us-east1 region.
    """

    try:
        # first create model
        create_model(model_name, project_id)

        # then create a version for that model
        create_model_version(model_name, model_version, project_id, deployment_uri)

    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()
