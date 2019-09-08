""" Resnet50 image encoder.

Returns the convolutional features of Resnet50.
"""
import logging
import numpy as np
import tensorflow as tf

from keras.preprocessing import image
from keras.applications.resnet50 import ResNet50
from keras.applications.resnet50 import preprocess_input
from keras.models import Model


class ResNet50ImageEncoder:
    def __init__(self, print_summary=True, top_layer='fc1000', include_top=True):
        base_model = ResNet50(weights='imagenet', include_top=include_top)
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer(top_layer).output)
        self.graph = tf.get_default_graph()
        if print_summary:
            self.model.summary()

    def batch_encode(self, img_paths):
        features = []
        for img_path in img_paths:
            features.append(self.encode(img_path))
        return features

    def encode(self, img_path, flattened=True):
        # Running predict on webservice, requires fetching tf.graph
        # See: https://github.com/keras-team/keras/issues/2397
        with self.graph.as_default():
            logging.info('Encode: {}'.format(img_path))
            img = image.load_img(img_path, target_size=(224, 224))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            feature = self.model.predict(img_data)
            feature_np = np.array(feature)
            return feature_np.flatten() if flattened else feature_np
