from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model.signature_def_utils_impl import predict_signature_def
from keras.models import model_from_json
from keras import backend as K
#import pysnooper
import os
from google.cloud import error_reporting


#@pysnooper.snoop()
def to_savedmodel(keras_model, export_path):
    """
    Converts Keras model into a tensorflow saved_model format.
    :param keras_model: Loaded keras model
    :param export_path: local directory where you want to save your tensorflow SavedModel format model.
    :return: None. Creates directory and saved_model.pb file
    """
    try:
        builder = saved_model_builder.SavedModelBuilder(export_path)
        signature = predict_signature_def(
            inputs={'input': keras_model.inputs[0]},
            outputs={'output': keras_model.outputs[0]}
        )

        with K.get_session() as sess:
            builder.add_meta_graph_and_variables(
                sess=sess,
                tags=[tag_constants.SERVING],
                signature_def_map={
                    signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature
                }
            )
        builder.save()
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()

#@pysnooper.snoop()
def get_keras_model(h5_file, json_file, loss, optimizer, metrics):
    """
    Loads a Keras model from .h5 and .json file.
    :param h5_file: STRING. REQUIRED. path to .h5 model file
    :param json_file: STRING. REQUIRED. path to .json model file
    :param loss: REQUIRED. STRING. loss for model (ex: 'mean-squared-error') used to compile model
    :param optimizer: REQUIRED. STRING. optimizer for model (ex: 'Adam') used to compile model
    :param metrics: REQUIRED. ARRAY. metrics for model (ex: ['mean-squared-error'])
    :return: compiled keras model
    """
    try:
        with open(json_file, 'r') as f:
            json_model = f.read()
        model = model_from_json(json_model)
        model.load_weights(h5_file)
        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
        return model
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()

#@pysnooper.snoop()
def convert(h5_file, json_file, loss, optimizer, metrics, export_path):
    """
    Converts a keras model from .h5 and .json files to a Tensorflow SavedModel format model for AI platform predictions.
    :param h5_file: REQUIRED. STRING. path to .h5 model file.
    :param json_file: REQUIRED. STRING. path to .json model file.
    :param loss: REQUIRED. STRING. loss for model (ex: 'mean-squared-error') used to compile model (same as training loss)
    :param optimizer: REQUIRED. STRING. optimizer for model (ex: 'Adam') used to compile model (samle as training optimizer)
    :param metrics: REQUIRED. ARRAY. metrics for model (ex: ['mean-squared-error']) (same as training metrics)
    :param export_path: directory where saved_model.pb file will be exported to.
    :return: None. Creates export_path and export folder, with saved_model.pb file.
    """
    try:
        if (os.path.isdir(export_path)):
            os.removedirs(export_path)
        model = get_keras_model(h5_file, json_file, loss, optimizer, metrics)
        to_savedmodel(model, export_path)
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()


