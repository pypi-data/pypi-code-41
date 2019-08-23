"""Convenience module to assign a beauty score an image."""

import importlib_resources
from tutti_aisthetics import model
from tutti_aisthetics.nima import Nima
from logging import getLogger
from time import time


logger = getLogger(__name__)


class Scorer:
    """Scorer to assign beauty score to an image."""

    def __init__(self):

        self.version = '1.0.0'
        logger.debug('initialize scorer version %s', self.version)
        t0 = time()
        self._model = Nima()

        with importlib_resources.path(model, 'weights_aisthetics.hdf5') as path:
            self._model.load_weights(weights_file=path.as_posix())

        logger.debug('scorer initialized in %s seconds', round(time() - t0, 3))

    def score(self, image_path: str):
        """Score an image.

        :param image_path: Path (relative or absolute) to the image to be scored.
        :returns: A dictionary containing image path and the beauty score.
        """

        logger.debug('Score image %s', image_path)

        t0 = time()
        model_response = self._model.predict(images=[image_path], augmented=True)[0]
        scoring_time_seconds = round(time() - t0, 3)

        scorer_response = {
            'image': model_response['image'],
            'score': model_response['mean_score_prediction'],
            'scoring_time_seconds': scoring_time_seconds,
            'scorer_version': self.version
        }

        logger.debug('Image scored: %s', scorer_response)
        return scorer_response
