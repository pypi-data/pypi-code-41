import re

from coala_json.loader.coalaJsonLoader import coalaJsonLoader


class ResultReporter:
    """
    Every test report class is a sub class of ResultReporter
    """

    def __init__(self, loader: coalaJsonLoader, coala_json):
        self.loader = loader
        self.coala_json = coala_json
