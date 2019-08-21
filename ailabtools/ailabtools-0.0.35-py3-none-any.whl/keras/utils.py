import os, sys
import tensorflow as tf

def convert_keras_to_tflite(keras_model_path, tflite_output):
    converter = tf.contrib.lite.TFLiteConverter.from_keras_model_file(keras_model_path)
    tflite_quantized_model = converter.convert()
    with open(tflite_output, "wb") as tt:
        tt.write(tflite_quantized_model)