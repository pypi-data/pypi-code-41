"""Callback classes to use whilst training Keras models."""
import numpy as np


class SimilarityCallback(object):
    """
    Keras callback to identify the nearest k characters to a fixed set of
    evaluation characters based on embedding cosine similarity.
    """

    def __init__(self, k, evaluation_examples, text, model):
        """

        Parameters
        ----------
        k : int
            Number of nearest characters to identify.
        evaluation_examples : list of str
            Character set for which to identify the nearest characters.
        text : waddle.text_processing.Text
            The text over which the discrimination model is being trained
        model : tensorflow.keras.Model
            Model to calculate the cosine similarity between two characters.
        """
        self.top_k = k
        self.evaluation_examples = evaluation_examples
        self.text = text
        self.model = model

    def run_sim(self):
        """Identify nearest characters to the evalution set."""
        for character_index in self.evaluation_examples:
            character = self.text.index_to_character[character_index]

            sim = self._get_sim(character_index)
            nearest = (-sim).argsort()[1:self.top_k + 1]
            logging_output = 'Nearest to {}:'.format(character)

            for nearby_character_index in nearest:
                close_word = self.text.index_to_character[nearby_character_index]
                logging_output = '{} {},'.format(logging_output, close_word)

            print(logging_output)

    def _get_sim(self, valid_word_idx):
        target_array = np.ones((self.text.vocabulary_size,)) * valid_word_idx
        context_array = np.arange(self.text.vocabulary_size)

        return (
            self.model
            .predict_on_batch([target_array, context_array])
            .reshape(self.text.vocabulary_size)
        )
