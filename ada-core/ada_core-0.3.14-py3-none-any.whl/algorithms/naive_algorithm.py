from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType


class NaiveAlgorithm(Algorithm):

    def __init__(self):
        super(NaiveAlgorithm, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value):
        return input_value