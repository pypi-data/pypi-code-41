import os
import tensorflow as tf

def tf_mute_warning():
    """
    Make Tensorflow less verbose
    """
    try:

        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    except ImportError:
        pass
