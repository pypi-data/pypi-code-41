import numpy as np
import tensorflow as tf


def earth_movers_distance(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """ Computes the EMD (Earth Movers Distance) for a pair (y_true, y_pred) """
    cdf_true = tf.keras.backend.cumsum(y_true, axis=-1)
    cdf_pred = tf.keras.backend.cumsum(y_pred, axis=-1)
    emd = tf.keras.backend.sqrt(tf.keras.backend.mean(tf.keras.backend.square(cdf_true - cdf_pred), axis=-1))
    return tf.keras.backend.mean(emd)
