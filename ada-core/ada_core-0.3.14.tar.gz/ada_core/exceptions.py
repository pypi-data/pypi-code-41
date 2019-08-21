"""
Author: qiacai
"""


"""
Exception Classes
"""



class AlgorithmNotFound(Exception):

    """
    Raise when algorithm can not be found
    """
    pass


class AlgorithmOutputFormatError(Exception):

    """
    Raise when the output format of the algorithm is not correct
    """
    pass


class AlgorithmCalculationError(Exception):

    pass


class ParametersNotPassed(Exception):

    """
    Raise when algorithm can not be properly initialized because some required parameters are not passed in init.
    """
    pass


class InvalidDataFormat(Exception):

    """
    Raise when data has invalid format.
    """
    pass


class NotEnoughDataPoint(Exception):

    """
    Raise when there are not enough data points.
    """
    pass