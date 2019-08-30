'''
Created on Apr 16, 2019

@author: baumannt
'''

from abc import ABC, abstractmethod
import os
from tabulate import tabulate
import pandas as pd


class Drever(ABC):
    '''
    This is the drever base class. New Drever classes needs to be derived from
    this base class with an overwritten run method.

    When deriving your new Drever class, you have to set configuration
    parameters by using the CLASS_CONFIG dictionary. The "INPUT_VECTOR_TYPE"
    and the "OUTPUT_VECTOR_TYPE" needs to be defined. Valid values are classes,
    e.g. a Numpy array using "numpy.ndarray" or tuples of classes. If you don't
    care about the IN/OUT data types you can use the "ALL" string, which
    disables type checking (for an example see the Bypass class).
    '''

    # Overwrite this dictionary in your derived Drever class.
    CLASS_CONFIG = {
        "INPUT_VECTOR_TYPE":  None,
        "OUTPUT_VECTOR_TYPE": None
    }

    # Overwrite this dictionary with your default Drever algorithm parameters.
    DEFAULT_PARAMS = {}

    def __init__(self, params=None, input_data=None, dump_filename=None):
        '''
        Constructor
        '''
        if params is None:
            self.params = dict(self.DEFAULT_PARAMS)
        else:
            self.params = dict(params)

        self.dump_filename = None if dump_filename is None else dump_filename

        # Never use this variables without the getters and setters.
        self._input_data = None
        self._output_data = None

        if input_data is not None:
            self.set_input_data(input_data)

    @abstractmethod
    def run(self):
        '''
        This is the main method of your Drever instance. Overwrite the run
        method with your algorithm.
        '''

    @classmethod
    def dump_vectors(cls, path, vectors):
        '''
        This method stores the vector data. The dump can be used inside the
        HDL testbench for verification.

        Overwrite this method for proper vector dumping.
        '''
        assert vectors is not None, "Vector contains no data!"

        assert False, \
            "Vector dumpin not overloaded. No vector file was written to\n" \
            "Path:    " + path + "\n\n"

    def dump_input_vectors(self, path):
        '''
        Dumping input testvectors to file.
        '''
        self.dump_vectors(path, self.get_input_data())

    def dump_output_vectors(self, path):
        '''
        Dumping output testvectors to file.
        '''
        self.dump_vectors(path, self.get_output_data())

    def set_params(self, params):
        '''
        Parameter Setter
        '''
        self.params = params

    def get_params(self):
        '''
        Parameters Dictionary Getter
        '''
        return self.params

    def get_parameter(self, key, default):
        '''
        Parameter Getter: Returns the parameter with the given key from the
        parameter dictionary. If key is not found in it, default will be
        returned.
        '''
        if key in self.get_params():
            return self.get_params()[key]

        return default

    def print_params_table(self):
        '''
        Prints all set parameters in table form.
        '''
        if self.params == {}:
            output = \
                "+-----------------------------------+\n" + \
                "| No parameters available to print! |\n" + \
                "+-----------------------------------+"
        else:
            data_frame = pd.DataFrame({
                'Registers': list(self.params.keys()),
                'Values': list(self.params.values())
            })
            output = tabulate(data_frame, headers='keys', tablefmt='psql')

        print(output)

    def set_input_data(self, data):
        '''
        Setter for input vector data.
        '''

        if self.CLASS_CONFIG["INPUT_VECTOR_TYPE"] != "ALL":
            assert self.CLASS_CONFIG["INPUT_VECTOR_TYPE"] is not None, \
                "INPUT_VECTOR_TYPE of your derived Drever isn't set!"
            assert isinstance(data, self.CLASS_CONFIG["INPUT_VECTOR_TYPE"]), \
                "Input data can't be set, due invalid input data type!"

        self._input_data = data

    def get_input_data(self):
        '''
        Getter for input vector data.
        '''

        if self.CLASS_CONFIG["INPUT_VECTOR_TYPE"] != "ALL":
            assert isinstance(
                self._input_data,
                self.CLASS_CONFIG["INPUT_VECTOR_TYPE"]), \
                "Data can't be read, due the class' " \
                "input data has invalid type!"
        return self._input_data

    def _set_output_data(self, data):
        '''
        Setter for output vector data. This should only be used by derived
        classes.
        '''

        if self.CLASS_CONFIG["OUTPUT_VECTOR_TYPE"] != "ALL":
            assert self.CLASS_CONFIG["OUTPUT_VECTOR_TYPE"] is not None, \
                "OUTPUT_VECTOR_TYPE of your derived Drever isn't set!"
            assert isinstance(data, self.CLASS_CONFIG["OUTPUT_VECTOR_TYPE"]), \
                "Output data can't be set, due invalid input data type!"

        self._output_data = data

    def get_output_data(self):
        '''
        Getter for output vector data.
        '''

        if self.CLASS_CONFIG["OUTPUT_VECTOR_TYPE"] != "ALL":
            assert isinstance(
                self._output_data,
                self.CLASS_CONFIG["OUTPUT_VECTOR_TYPE"]), \
                "Data can't be read, due the class' output data has " \
                "invalid type! Maybe run() method wasn't called yet?"

        return self._output_data

    def set_dump_filename(self, dump_filename):
        '''
        Setter for the vector dump filename.
        '''
        assert dump_filename, "Non valid filename string"
        self.dump_filename = dump_filename

    def vunit_get_dump_filename(self, data=None):
        '''
        Getter for input or output dump filename.
        '''

        assert data in ("input", "output", None), \
            "Data source for dump file not know!"

        default = "output"
        result = ""

        if data == "input":
            result = data + "_" + self.dump_filename
        else:
            result = default + "_" + self.dump_filename

        return result

    # This is covered within the HDL tests
    def vunit_pre_config(self, output_path):  # pragma: no cover
        '''
        VUnit preconfiguration dumps input vector file, runs algorithm and
        dumps output vector files.
        '''
        stimulus_filename = os.path.join(
            output_path,
            self.vunit_get_dump_filename("input")
        )
        processed_filename = os.path.join(
            output_path,
            self.vunit_get_dump_filename("output")
        )

        self.dump_input_vectors(stimulus_filename)
        self.run()
        self.dump_output_vectors(processed_filename)

        return True

    # This is covered within the HDL tests
    def vunit_post_check(self, output_path):  # pragma: no cover
        '''
        Placeholder for future implementations.
        '''
        return False

    def vunit_generate_generics(self):
        '''
        VUnit HDL Generics generator.
        '''
        return dict(
            IN_FILENAME=self.vunit_get_dump_filename("input"),
            OUT_FILENAME=self.vunit_get_dump_filename("output")
        )
