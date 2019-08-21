"""
Author: qiacai

UnaryJudger: deal with the cases where only have one input

"""
from ada_core import exceptions
from ada_core.base_handler import BaseHandler
from ada_core.data_model.io_data_type import AlgorithmIODataType


class Handler(BaseHandler):
    def __init__(self, algorithm_name, handler_input, algorithm_input_type=None, algorithm_output_type=None,
                 params=None):
        super(Handler, self).__init__(algorithm_name=algorithm_name, handler_input=handler_input, algorithm_input_type=algorithm_input_type,
                                            algorithm_output_type=algorithm_output_type, params=params)

    def _parse_handler_input(self):
        pass


#
# class UnaryJudger(UnaryHandler):
#
#     def _parse(self):
#         super(UnaryHandler, self)._parse()
#
#         if self.algorithm_output_type != AlgorithmIODataType.BOOL.value:
#             raise exceptions.ParametersNotPassed(
#                 'the algorithm_output_type is not Bool, please change to other handlers')