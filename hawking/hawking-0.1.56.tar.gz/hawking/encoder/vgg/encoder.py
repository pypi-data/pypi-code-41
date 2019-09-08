""" VGG16 image encoder.

Returns the convolutional features of VGG16/VGG19.
tutorial: https://keras.io/applications/.
"""
import numpy as np
import tensorflow as tf

from keras.preprocessing import image
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.vgg19 import preprocess_input
from keras.models import Model


class VGG16ImageEncoder:
    """ VGG16 Image Encoder with default 'fc1' top layer. """
    def __init__(self, top_layer='fc1', print_summary=False):
        base_model = VGG16(weights='imagenet')
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer(top_layer).output)
        self.graph = tf.get_default_graph()
        if print_summary:
            self.model.summary()

    def batch_encode(self, img_paths):
        """ Batch encode images into VGG16 embedding features. """
        features = []
        for img_path in img_paths:
            features.append(self.encode(img_path))
        return features

    def encode(self, img_path):
        """ Encode an image into VGG16 embedding features. """
        # Running predict on webservice, requires fetching tf.graph
        # See: https://github.com/keras-team/keras/issues/2397
        with self.graph.as_default():
            img = image.load_img(img_path, target_size=(224, 224))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            feature = self.model.predict(img_data)
            feature_np = np.array(feature)
            return feature_np.flatten()


class VGG19ImageEncoder:
    """ VGG19 Image Encoder with default 'fc1' top layer. """
    def __init__(self, top_layer='fc1', print_summary=False):
        base_model = VGG19(weights='imagenet')
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer(top_layer).output)
        self.graph = tf.get_default_graph()
        if print_summary:
            self.model.summary()

    def batch_encode(self, img_paths):
        """ Batch encode images into VGG19 embedding features. """
        features = []
        for img_path in img_paths:
            features.append(self.encode(img_path))
        return features

    def encode(self, img_path, flattened=False):
        """ Encode an image into VGG19 embedding features. """
        # Running predict on webservice, requires fetching tf.graph
        # See: https://github.com/keras-team/keras/issues/2397
        with self.graph.as_default():
            img = image.load_img(img_path, target_size=(224, 224))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            feature = self.model.predict(img_data)
            feature_np = np.array(feature)
            return feature_np.flatten() if flattened else feature_np
