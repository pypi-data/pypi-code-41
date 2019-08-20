import logging
import pathlib
import warnings
from typing import Any, Callable, Dict, List, Union

import numpy as np
from sklearn import model_selection

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=FutureWarning)
    import tensorflow as tf
    from tutti_aisthetics import data_generator, keras_utils, losses, utils

logger = logging.getLogger(__name__)


class Nima:
    """
    This class implements the architecture of the NIMA neural network
    """
    n_classes: int
    learning_rate: float
    dropout_rate: float
    loss: Callable[[np.ndarray, np.ndarray], np.ndarray]
    decay: float
    weights: str
    input_height: int
    input_width: int
    base_nn: tf.keras.Model
    nn: tf.keras.Model

    def __init__(self,
                 n_classes: int = 10,
                 learning_rate: float = 0.001,
                 dropout_rate: float = 0,
                 input_height: int = 224,
                 input_width: int = 224,
                 loss: Callable[[np.ndarray, np.ndarray], np.ndarray] = losses.earth_movers_distance,
                 decay: float = 0,
                 weights: str = 'imagenet') -> None:
        """
        Constructor of the class

        :param n_classes: indicates the number of possible classes (scores) to classify
        :param learning_rate: learning rate for the NN
        :param dropout_rate: dropout rate for the NN
        :param loss: which loss function to use
        :param weights: weights to use for the model
        """
        self.n_classes = n_classes
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.loss = loss
        self.decay = decay
        self.weights = weights
        self.input_height = input_height
        self.input_width = input_width

        # Build neural net: base model
        logger.debug('Building base neural net: MobileNet')
        self.base_nn = tf.keras.applications.mobilenet.MobileNet(
            input_shape=(self.input_height, self.input_width, 3),
            weights=self.weights, include_top=False,
            pooling='avg')
        # Build neural net: stack a dropout and a dense layers on top of base model
        logger.debug('Stacking dropout and dense layers over base model')
        self.nn = tf.keras.Sequential(layers=[
            # base model: MobileNet (93 - 6 = 87 layers). The 6 layers removed are the top layers for ImageNet
            *self.base_nn.layers,
            # Extra layer: dropout
            tf.keras.layers.Dropout(rate=self.dropout_rate),
            # Output layer: dense with softmax activation for 10 classes
            tf.keras.layers.Dense(units=self.n_classes, activation='softmax')
        ])

    def compile(self) -> None:
        """ Prepare model for training """
        logger.debug('Compiling NIMA model')
        self.nn.compile(optimizer=tf.keras.optimizers.Adam(lr=self.learning_rate, decay=self.decay),
                        loss=self.loss)

    @property
    def preprocessing_function(self) -> Callable:
        """ Returns the specific model (MobileNet) pre-processing function """
        return tf.keras.applications.mobilenet.preprocess_input

    def predict(self, images: List[str], augmented: bool = False
                ) -> Union[List[np.ndarray], List[Dict[str, Union[str, Any]]]]:
        """
        Predict routine. Can output simple probabilities or augmented information (mean score, sd).
        The mean score and standard deviation is not simply the mean of the class probabilities. They're computed
        as the mean value of a histogram with the probabilities as counts and the score (1 to 10) as values.

        :param images: path to image (or list of paths to several images) to score
        :param augmented: flag that determines if the output are simple class probabilities (for the
        1 to 10 integer scores) or augmented data (file name, class probabilities, mean score and standard
        deviation)
        :return: either a list of np.arrays or a list of dicts with augmented data
        """
        # Fix in case the input is a string and not a list
        if isinstance(images, str):
            images = [images]

        results = []
        for img in images:
            logger.debug('Pre-processing image %s', img)
            x = np.empty((1, self.input_height, self.input_width, 3))
            x[0,] = np.asarray(
                tf.keras.preprocessing.image.load_img(img, target_size=(self.input_height, self.input_width)))
            x = self.preprocessing_function(x)
            logger.debug('Scoring image %s', img)
            results.append(self.nn.predict_proba(x)[0])

        if augmented:
            augmented_results = [{
                'image': img,
                'predictions': results[i].tolist(),
                'mean_score_prediction': utils.calc_mean_score(results[i]),
                'sd_score_prediction': utils.calc_sd_score(results[i])
            } for i, img in enumerate(images)]
            return augmented_results

        return results

    def load_weights(self, weights_file: str) -> None:
        self.nn.load_weights(weights_file)

    def train(self, samples: List[Dict[str, Any]],
              image_dir: str,
              job_dir: str,
              batch_size: int = 96,
              epochs_train_dense: int = 5,
              learning_rate_dense: float = 0.001,
              decay_dense: float = 0,
              epochs_train_all: int = 9,
              learning_rate_all: float = 0.00003,
              decay_all: float = 0.000023,
              image_format: str = 'jpg',
              existing_weights: str = None,
              multiprocessing_data_load: bool = True,
              num_workers_data_load: int = 4,
              test_size: float = 0.05):
        """
        Train a NIMA neural network (either from scratch or transfering from previous weights) to generate a new model
        weights file in hdf5 format.

        :param samples: samples, a list of dicts like
                [
                  {
                    "image_id": "231893",
                    "label": [2,8,19,36,76,52,16,9,3,2]
                  },
                  {
                    "image_id": "746672",
                    "label": [1,2,7,20,38,52,20,11,1,3]
                  },
                  ...
                ]
            (usually they will be loaded from a JSON file with tutti_aisthetics.utils.load_json()
        :param image_dir: directory where images are stored
        :param batch_size: size of train batches
        :param epochs_train_dense: number of epochs to train dense layers
        :param learning_rate_dense: learning rate for first training step (dense layers)
        :param decay_dense: decay rate for first training step (dense layers)
        :param epochs_train_all: number of training epochs for second training step (all layers)
        :param learning_rate_all: learning rate for second training step (all layers)
        :param decay_all: decay rate for other layers
        :param job_dir: working directory for the training job
        :param image_format: format of images (jpg by default)
        :param existing_weights: if not None, then start training from a given weights set
        :param multiprocessing_data_load: flag to enable multiprocessing
        :param num_workers_data_load: number of workers to use if multiprocessing is enabled
        :param test_size: percentage of the train dataset used for validation
        :return: Nothing
        """

        if existing_weights is not None:
            self.nn.load_weights(existing_weights)

        samples_train, samples_test = model_selection.train_test_split(samples, test_size=test_size, shuffle=True,
                                                                       random_state=42)

        training_generator = data_generator.TrainDataGenerator(samples_train, image_dir, batch_size, self.n_classes,
                                                               self.preprocessing_function, image_format=image_format)
        validation_generator = data_generator.TestDataGenerator(samples_test, image_dir, batch_size, self.n_classes,
                                                                self.preprocessing_function, image_format=image_format)

        # initialize callbacks TensorBoardBatch and ModelCheckpoint
        tensorboard_callback = keras_utils.TensorBoardBatch(log_dir=pathlib.Path(job_dir) / 'logs')

        model_save_name = 'weights_mobilenet_{epoch:02d}_{val_loss:.3f}.hdf5'
        model_file_path = pathlib.Path(job_dir) / 'weights' / model_save_name
        model_checkpointer = tf.keras.callbacks.ModelCheckpoint(filepath=model_file_path, monitor='val_loss', verbose=1,
                                                                save_best_only=True, save_weights_only=True)
        # start training dense layers
        for layer in self.base_nn.layers:
            layer.trainable = False

        self.learning_rate = learning_rate_dense
        self.decay = decay_dense
        self.compile()
        self.nn.summary(print_fn=logger.info)

        self.nn.fit_generator(generator=training_generator, validation_data=validation_generator,
                              epochs=epochs_train_dense, verbose=1, use_multiprocessing=multiprocessing_data_load,
                              workers=num_workers_data_load, max_queue_size=30,
                              callbacks=[tensorboard_callback, model_checkpointer])

        # start training all layers
        for layer in self.base_nn.layers:
            layer.trainable = True

        self.learning_rate = learning_rate_all
        self.decay = decay_all
        self.compile()
        self.nn.summary(print_fn=logger.info)

        self.nn.fit_generator(generator=training_generator, validation_data=validation_generator,
                              epochs=epochs_train_dense + epochs_train_all, initial_epoch=epochs_train_dense, verbose=1,
                              use_multiprocessing=multiprocessing_data_load, workers=num_workers_data_load,
                              max_queue_size=30, callbacks=[tensorboard_callback, model_checkpointer])

        tf.keras.backend.clear_session()


def get_aisthetics_model() -> Nima:
    """
    Helper function that creates a NIMA object and loads the weights provided by
    the package

    :return: the NIMA neural net with weights
    """
    weights_path = pathlib.Path(__file__).parent.resolve() / 'model' / 'weights_aisthetics.hdf5'
    model = Nima()
    logger.debug('Attempting to retreive weights file %s', str(weights_path))
    model.load_weights(str(weights_path))
    return model
