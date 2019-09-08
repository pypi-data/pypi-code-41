""" InceptionResNetV2 image encoder.

Returns the convolutional features of inception_resnet_v2.
"""
import logging
import numpy as np
import tensorflow as tf

from keras.preprocessing import image
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.applications.inception_resnet_v2 import preprocess_input
from keras.models import Model


class InceptionResNetV2ImageEncoder:
    def __init__(self, print_summary=True, top_layer='predictions', include_top=True):
        base_model = InceptionResNetV2(weights='imagenet', include_top=include_top)
        base_model.summary()
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
            img = image.load_img(img_path, target_size=(299, 299))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            feature = self.model.predict(img_data)
            feature_np = np.array(feature)
            return feature_np.flatten() if flattened else feature_np
