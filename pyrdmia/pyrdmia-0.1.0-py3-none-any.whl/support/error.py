
"""Error classes module

All error classes used in the IntPy package are centralized here.
"""


class IntervalError(ValueError):
    """Generic error involving intervals

    This can be raised in a context involving intervals where there's no other
    more specialized error class to describe the problem.
    """

class IntervalDivisionByZero(IntervalError):
    def __init__(self,msg=None):
        if msg is None:
            IntervalError.__init__(self,"Your denominator contains zero.")


class TypeIntervalError(IntervalError):
    def __init__(self,msg=None):
        if msg is None:
            IntervalError.__init__(self,"Operation not defined for RDM-IA, please check the right data")


class UndefinedValueIntervalError(IntervalError):
    def __init__(self,msg=None):
        if msg is None:
            IntervalError.__init__(self,"The interval not be empty.")
        else:
            IntervalError.__init__(self, msg)