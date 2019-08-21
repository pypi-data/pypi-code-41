"""
Author: qiacai
"""


__all__ = ['binary_judge_algorithms', 'binary_calculate_algorithms', 'unary_common_calculate_algorithms', 'unary_ts2num_calculate_algorithms', 'unary_ts2ts_calculate_algorithms',
           'unary_judge_algorithms']


class Algorithm(object):
    """
    Base class for Algorithm
    """

    def __init__(self, class_name):
        self.class_name = class_name
        # self.input_type = None
        # self.output_type = None
        # self.name = 'algorithm'

    def _run_algorithm(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        # todo: think about put input validation here
        return self._run_algorithm(*args, **kwargs)

    def get_output(self, *args, **kwargs):
        return self.run(*args, **kwargs).get('output_value')

    # def getName(self):
    #     return self.name
    #
    # def getClass(self):
    #     return self.class_name
    #
    # def getInputType(self):
    #     return self.input_type
    #
    # def getOutputType(self):
    #     return self.output_type