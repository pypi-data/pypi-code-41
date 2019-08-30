'''
Created on Apr 26, 2019

@author: baumannt
'''
from drever.base_class import Drever


class Bypass(Drever):
    '''
    classdocs
    '''

    CLASS_CONFIG = {
        "INPUT_VECTOR_TYPE":  "ALL",
        "OUTPUT_VECTOR_TYPE": "ALL"
    }

    def run(self):
        '''
        The Bypass Drever simply sets the output data as the Input Data
        '''
        self._set_output_data(self.get_input_data())
