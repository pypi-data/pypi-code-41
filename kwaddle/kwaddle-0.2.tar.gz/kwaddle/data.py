import pickle
import numpy as np
from tensorflow.keras.preprocessing.sequence import skipgrams


class TrainingData(object):

    def __init__(self, target, context, labels):
        """
        Data needed to train the context discrimination model.

        Parameters
        ----------
        target : np.ndarray
            Encoded target character.
        context : np.ndarray
            Encoded character of possible context character.
        labels : np.ndarray
            Positive or negative label indicating whether context character was
            truly found within the context of the target character.
        """
        self.target = target
        self.context = context
        self.labels = labels

    @classmethod
    def from_text(cls, text, window_size):
        """
        Generate context-based training data from a text string.

        Builds a training dataset that can be used to identify whether two
        characters are found within a certain window of each other.

        Parameters
        ----------
        text : text.Text
        window_size : int

        Returns
        -------
        This object.
        """
        couples, labels = skipgrams(
            text.encode_text(), text.vocabulary_size, window_size=window_size)
        target, context = zip(*couples)
        return cls(
            np.array(target, dtype='int32'),
            np.array(context, dtype='int32'),
            np.array(labels, dtype='int32')
        )

    def dump(self, path):
        """Dump the data to file."""
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        """Load the data from file."""
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj
