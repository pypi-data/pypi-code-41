"""
Author: qiacai
"""


from ada_core.algorithms import Algorithm
from ada_core import exceptions
from ada_core.data_model.io_data_type import AlgorithmIODataType


class BaseBinaryNum1NumJudgeAlgorithm(Algorithm):
    def __init__(self, class_name):
        """
        Initializer

        :return:
        """

        super(BaseBinaryNum1NumJudgeAlgorithm, self).__init__(class_name=class_name)
        # self.name = 'base_binary_judge'
        # self.input_type = AlgorithmIODataType.BINARY_NUMBER_INPUT.value
        # self.output_type = AlgorithmIODataType.BOOL.value

    def _run_algorithm(self, **kwargs):
        raise NotImplementedError


class EqualBinaryJudgeAlgorithm(BaseBinaryNum1NumJudgeAlgorithm):
    def __init__(self):
        super(EqualBinaryJudgeAlgorithm, self).__init__(self.__class__.__name__)
        # self.name = '=='

    def _run_algorithm(self, input_value):
        if input_value.left == input_value.right:
            return True
        else:
            return False


class GreaterThanBinaryJudgeAlgorithm(BaseBinaryNum1NumJudgeAlgorithm):
    def __init__(self):
        super(GreaterThanBinaryJudgeAlgorithm, self).__init__(self.__class__.__name__)
        # self.name = '>'

    def _run_algorithm(self, input_value):
        if input_value.left > input_value.right:
            return True
        else:
            return False


class GreaterThanOrEqualBinaryJudgeAlgorithm(BaseBinaryNum1NumJudgeAlgorithm):
    def __init__(self):
        super(GreaterThanOrEqualBinaryJudgeAlgorithm, self).__init__(self.__class__.__name__)
        # self.name = '>='

    def _run_algorithm(self, input_value):
        if input_value.left >= input_value.right:
            return True
        else:
            return False


class LessThanBinaryJudgeAlgorithm(BaseBinaryNum1NumJudgeAlgorithm):
    def __init__(self):
        super(LessThanBinaryJudgeAlgorithm, self).__init__(self.__class__.__name__)
        # self.name = '<'

    def _run_algorithm(self, input_value):
        if input_value.left < input_value.right:
            return True
        else:
            return False


class LessThanOrEqualBinaryJudgeAlgorithm(BaseBinaryNum1NumJudgeAlgorithm):
    def __init__(self):
        super(LessThanOrEqualBinaryJudgeAlgorithm, self).__init__(self.__class__.__name__)
        # self.name = '<='

    def _run_algorithm(self, input_value):
        if input_value.left <= input_value.right:
            return True
        else:
            return False