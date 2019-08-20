from googleapiclient import discovery
import json
#import pysnooper


#@pysnooper.snoop()
def predict(model_name, project, data, model_version=None):
    """
    Makes API call to AI Platform and returns prediction.
    :param model_name: REQUIRED. STRING. Name of model on AI Platform.
    :param project: your project Id.
    :param data: cleaned and preprocessed data in shape that your model expects in JSON format "{instances: [data]}"
    :param model_version: model version you want to make the request to
    :return: prediction:
    """
    project_id = f"projects/{project}"
    service = discovery.build('ml', 'v1')
    name = f"{project_id}/models/{model_name}"
    if model_version is not None:
        name += f"/versions/{model_version}"
    data_pred = json.loads(data)
    instances = data_pred['instances']

    try:
        response = service.projects().predict(
            name=name,
            body={"instances": instances}
        ).execute()
        print(response['predictions']) # example prediction = [{'output': [0.4796813130378723]}]
        return response['predictions']
    except:
        print(response['error'])

