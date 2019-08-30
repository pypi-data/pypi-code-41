'''
Created on Apr 26, 2019

@author: baumannt
'''

from drever.base_class import Drever
from drever.data_handlers.image import ImageData


class VideoFilter(Drever):
    '''
    classdocs
    '''

    CLASS_CONFIG = {
        "INPUT_VECTOR_TYPE":  (ImageData, ),
        "OUTPUT_VECTOR_TYPE": (ImageData, )
    }

    # Overwrite this dictionary with your default Drever algorithm parameters.
    DEFAULT_PARAMS = {}

    def run(self):
        self._set_output_data(self.get_input_data())

    @classmethod
    def dump_vectors(cls, path, vectors):
        vectors.save(path, False)
