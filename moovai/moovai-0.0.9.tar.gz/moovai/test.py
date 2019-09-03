
# import pandas as pd
# import sys
# sys.path.append('.')
# sys.path.append('..')
# import pysnooper
# import json
# from ml import get_prediction
# from ml import keras_to_savedmodel, get_prediction, create_model_ai_platform
# from ml.data.postprocess import Postprocess
# from ml.data.preprocess import Preprocess
# from google_cloud import cloud_storage
# import joblib
# import numpy as np

# project = 'currencyprediction'
# dataset_id = 'PR_International'

# json_input_file = 'input-values.json'
# scaler_uri = "gs://pr_international/ML/Scaler/scaler.pkl"
# almd_scaler_uri = "gs://pr_international/ML/Scaler/scaler_almd_index.pkl"
# #json_input_file = 'ml/input-model.json'
# #input= pd.read_csv('ml/input-model2.csv', index_col=0)

# input = pd.read_csv("ML_Pred_data_input_sample_2019-07-31.csv")

# scaler_file = cloud_storage.download_file_gcs(scaler_uri)
# scaler = joblib.load(scaler_file)
# almd_scaler_file = cloud_storage.download_file_gcs(almd_scaler_uri)
# almd_scaler = joblib.load(almd_scaler_file)


# class NumpyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return json.JSONEncoder.default(self, obj)

# @pysnooper.snoop()
# def predict():
#     predictions = []
#     models = ["model1", "model2", "model4", "model6"]
#     for model_name in models:
#         dict = {}
#         preprocess = Preprocess(scaler)
#         data_preprocessed = preprocess.apply_scaler(input) #np array shape [240, 266]
#         print(data_preprocessed)
#         data_json = json.dumps({"instances": [data_preprocessed]}, cls=NumpyEncoder)
#         prediction = get_prediction.predict(model_name, project, data_json)
#         output = [prediction[0]['output']]

#         post_processed = Postprocess(almd_scaler)
#         inv_transform = post_processed.inverse_transform(output)
#         price = -0.84029735 + 0.01082085*inv_transform

#         print(inv_transform)
#         print(price)
#         dict["model"] = model_name
#         dict["pred_index"] = inv_transform
#         dict["pred_price"] = price
#         predictions.append(dict)

#     print(predictions)

def test_docker():
    print("Hello, this is docker from toolbox!")


test_docker()
# def create_models():
#     models = ["model1"]
#     #, "model4", "model6"]
#
#     for model in models:
#         create_model_ai_platform.create_model(model, project)
#
#
# def create_model_version():
#     models = ["model4", "model6"]
#     base_deployment = "gs://pr_international/ML/models/AI_platform_models"
#     for model in models:
#         version_name = 'v1'
#         deployment_uri = f"{base_deployment}/{model}"
#         create_model_ai_platform.create_model(model, project)
#         create_model_ai_platform.create_model_version(model, version_name, project, deployment_uri)
#
# create_model_version()