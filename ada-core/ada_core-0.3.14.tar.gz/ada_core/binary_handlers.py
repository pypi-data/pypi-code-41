"""
Author: qiacai

UnaryJudger: deal with the cases where only have one input

"""
from ada_core import exceptions
from ada_core.base_handler import BaseHandler
from ada_core.data_model.io_data_type import AlgorithmIODataType


class BinaryHandler(BaseHandler):
    def _parse_handler_input(self, left_handler_input, right_handler_input):
        self.handler_input = {'left': left_handler_input, 'right': right_handler_input}

    def _parse(self, left_handler_input, right_handler_input):
        super(BinaryHandler, self)._parse(left_handler_input, right_handler_input)

    def _handle(self, left_handler_input, right_handler_input):
        super(BinaryHandler, self)._handle(left_handler_input, right_handler_input)

    def __init__(self, algorithm_name, left_handler_input, right_handler_input, algorithm_input_type=None,
                 algorithm_output_type=None, params=None):
        super(BinaryHandler, self).__init__(algorithm_name=algorithm_name, algorithm_input_type=algorithm_input_type,
                                            algorithm_output_type=algorithm_output_type, params=params,
                                            left_handler_input=left_handler_input, right_handler_input=right_handler_input)


class BinaryTsTsHandler(BinaryHandler):
    def __init__(self, algorithm_name, left_ts, right_ts, algorithm_input_type=None, algorithm_output_type=None, params=None):
        super(BinaryTsTsHandler, self).__init__(algorithm_name=algorithm_name, left_handler_input=left_ts,
                                                right_handler_input=right_ts, algorithm_input_type=algorithm_input_type,
                                                algorithm_output_type=algorithm_output_type, params=params)

    def _parse(self, left_handler_input, right_handler_input):
        super(BinaryTsTsHandler, self)._parse(left_handler_input, right_handler_input)

        if self.algorithm_input_type != AlgorithmIODataType.BINARY_TS_INPUT.value:
            raise exceptions.ParametersNotPassed(
                'the left_ts or right_ts could not form time series, please change to other handlers')


class BinaryNumTsHandler(BinaryHandler):
    def __init__(self, algorithm_name, left_num, right_ts, algorithm_input_type=None, algorithm_output_type=None, params=None):
        super(BinaryNumTsHandler, self).__init__(algorithm_name=algorithm_name, left_handler_input=left_num,
                                                 right_handler_input=right_ts, algorithm_input_type=algorithm_input_type,
                                                 algorithm_output_type=algorithm_output_type, params=params)

    def _parse(self, left_handler_input, right_handler_input):
        super(BinaryNumTsHandler, self)._parse(left_handler_input, right_handler_input)

        if self.algorithm_input_type != AlgorithmIODataType.BINARY_TS_NUM_INPUT.value:
            raise exceptions.ParametersNotPassed(
                'the left_num is not numeric, or the right_ts could not form time series, please change to other handlers')


class BinaryNumNumHandler(BinaryHandler):
    def __init__(self, algorithm_name, left_num, right_num, algorithm_input_type=None, algorithm_output_type=None, params=None):
        super(BinaryNumNumHandler, self).__init__(algorithm_name=algorithm_name, left_handler_input=left_num,
                                                  right_handler_input=right_num, algorithm_input_type=algorithm_input_type,
                                                  algorithm_output_type=algorithm_output_type, params=params)

    def _parse(self, left_handler_input, right_handler_input):
        super(BinaryNumNumHandler, self)._parse(left_handler_input, right_handler_input)

        if self.algorithm_input_type != AlgorithmIODataType.BINARY_NUM_INPUT.value:
            raise exceptions.ParametersNotPassed(
                'the left_num or right_num is not numeric, please change to other handlers')
