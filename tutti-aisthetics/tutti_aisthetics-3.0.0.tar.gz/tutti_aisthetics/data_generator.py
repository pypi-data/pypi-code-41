"""
This module serves as a helper to create generators that can feed with training or testing data to the Nima
model for training and testing purposes
"""
import pathlib
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import tensorflow as tf

from tutti_aisthetics import utils


class TrainDataGenerator(tf.keras.utils.Sequence):
    """ 
    This class prepares local data (images) for training the NIMA neural net.
    Inherits from Keras Sequence base object, allows to use multiprocessing in .fit_generator
    """
    samples: List[Dict[str, Any]]
    img_dir: str
    batch_size: int
    n_classes: int
    basenet_preprocess: Callable
    image_format: str
    image_load_dims: Tuple[int, int]
    image_crop_dims: Tuple[int, int]
    shuffle: bool
    indexes: np.ndarray

    def __init__(self, samples: List[Dict[str, Any]], img_dir: str, batch_size: int, n_classes: int,
                 basenet_preprocess: Callable, image_format: str, image_load_dims: Tuple[int, int] = (256, 256),
                 image_crop_dims: Tuple[int, int] = (224, 224), shuffle: bool = True):
        """
        Constructor for class TrainDataGenerator.
        """
        self.samples = samples
        self.img_dir = img_dir
        self.batch_size = batch_size
        self.n_classes = n_classes
        self.basenet_preprocess = basenet_preprocess  # Keras basenet specific preprocessing function
        self.image_load_dims = image_load_dims  # dimensions that images get resized into when loaded
        self.image_crop_dims = image_crop_dims  # dimensions that images get randomly cropped to
        self.shuffle = shuffle
        self.image_format = image_format
        self.on_epoch_end()  # call ensures that samples are shuffled in first epoch if shuffle is set to True

    def __len__(self) -> int:
        """ Call len() on this class to get the number of batches per epoch """
        return int(np.ceil(len(self.samples) / self.batch_size))  # number of batches per epoch

    def __getitem__(self, index: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns a subset of the labelled data

        :param index: batch index (can contain several samples)
        :return: two arrays, data and labels
        """
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]  # get batch indexes
        batch_samples = [self.samples[i] for i in batch_indexes]  # get batch samples
        x, y = self.__data_generator(batch_samples)
        return x, y

    def on_epoch_end(self) -> None:
        """ 
        Reindex the samples after each epoch.
        Shuffle samples after an epoch if self.shuffle
        """
        self.indexes = np.arange(len(self.samples))
        if self.shuffle is True:
            np.random.shuffle(self.indexes)

    def __data_generator(self, batch_samples: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """ Generate a batch of data, applying random crops and horizontal flips for helping the training """
        # initialize images and labels tensors for faster processing
        x = np.empty((len(batch_samples), *self.image_crop_dims, 3))
        y = np.empty((len(batch_samples), self.n_classes))

        for i, sample in enumerate(batch_samples):
            # load and randomly augment image
            img_file = pathlib.Path(self.img_dir) / '{}.{}'.format(sample['image_id'], self.image_format)
            img = utils.load_image(img_file, self.image_load_dims)
            if img is not None:
                img = utils.random_crop(img, self.image_crop_dims)
            img = utils.random_horizontal_flip(img)
            x[i,] = img

            # normalize labels
            y[i,] = utils.normalize_labels(sample['label'])

            # apply basenet specific preprocessing
            # input is 4D numpy array of RGB values within [0, 255]
            x = self.basenet_preprocess(x)

        return x, y


class TestDataGenerator(tf.keras.utils.Sequence):
    """ 
    This class prepares local data (images) for testing the NIMA neural net.
    Inherits from Keras Sequence base object, allows to use multiprocessing in .fit_generator
    """
    samples: List[Dict[str, Any]]
    image_dir: str
    batch_size: int
    n_classes: int
    basenet_preprocess: Callable
    image_format: str
    image_load_dims: Tuple[int, int]
    indexes: np.ndarray

    def __init__(self, samples: List[Dict[str, Any]], img_dir: str, batch_size: int, n_classes: int,
                 basenet_preprocess: Callable, image_format: str, image_load_dims: Tuple[int, int] = (224, 224)):
        """
        Constructor for class TestDataGenerator.
        """
        self.samples = samples
        self.image_dir = img_dir
        self.batch_size = batch_size
        self.n_classes = n_classes
        self.basenet_preprocess = basenet_preprocess  # Keras basenet specific preprocessing function
        self.image_load_dims = image_load_dims  # dimensions that images get resized into when loaded
        self.image_format = image_format
        self.on_epoch_end()  # call ensures that samples are shuffled in first epoch if shuffle is set to True

    def __len__(self) -> int:
        """ Call len() on this class to get the number of batches per epoch """
        return int(np.ceil(len(self.samples) / self.batch_size))  # number of batches per epoch

    def __getitem__(self, index: int) -> Tuple[np.ndarray, np.ndarray]:
        """ Returns a subset of the labelled data """
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]  # get batch indexes
        batch_samples = [self.samples[i] for i in batch_indexes]  # get batch samples
        x, y = self.__data_generator(batch_samples)
        return x, y

    def on_epoch_end(self) -> None:
        """ Reindex the samples after each epoch."""
        self.indexes = np.arange(len(self.samples))

    def __data_generator(self, batch_samples: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """ Generate a batch of data """
        # initialize images and labels tensors for faster processing
        x = np.empty((len(batch_samples), *self.image_load_dims, 3))
        y = np.empty((len(batch_samples), self.n_classes))

        for i, sample in enumerate(batch_samples):
            # load and randomly augment image
            img_file = pathlib.Path(self.image_dir) / '{}.{}'.format(sample['image_id'], self.image_format)
            img = utils.load_image(img_file, self.image_load_dims)
            if img is not None:
                x[i,] = img

            # normalize labels
            if sample.get('label') is not None:
                y[i,] = utils.normalize_labels(sample['label'])

        # apply basenet specific preprocessing
        # input is 4D numpy array of RGB values within [0, 255]
        x = self.basenet_preprocess(x)

        return x, y
