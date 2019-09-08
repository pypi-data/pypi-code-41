from ..core import Rdmia as rdmia
from ..core import Rdm
from .QualitativeMetrics import QualitativeMetrics as qm
import math


class RMath(object):

    '''
    def __init__(self):
        self.E = rdmia.number(math.e)
        self.PI = rdmia.number(math.pi)
    '''
    
    @staticmethod
    def exp(value):
        E = rdmia.number(math.e)**value
        return E
    
    @staticmethod
    def pi():
        PI = rdmia.number(math.pi)
        return PI
    
    @staticmethod
    def e():
        euler = rdmia.number(math.e)
        return euler
        
    #convert angle x from degrees to radians
    @staticmethod
    def degToRad(value):
        rad = 0.0
        if (type(value) is Rdm.Rdm):
            lower = math.radians(value.lower())
            upper = math.radians(value.upper())
            rad = rdmia.number(lower,upper)
        else:
            rad = rdmia.number(math.radians(value))
        return rad

    #convert angle x from radians to degrees
    @staticmethod
    def radToDeg(value):
        deg = 0.0
        if (type(value) is Rdm.Rdm):
            lower = math.degrees(value.lower())
            upper = math.degrees(value.upper())
            deg = rdmia.number(lower,upper)
        else:
            deg = rdmia.number(math.degrees(value))
        return deg

    #factorial
    @staticmethod
    def factorial(value):
        if (type(value) is Rdm.Rdm):
            lower = math.factorial(value.lower())
            upper = math.factorial(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.factorial(value))
        
    #natural logarithm
    @staticmethod
    def log(value):
        if (type(value) is Rdm.Rdm):
            lower = math.log(value.lower())
            upper = math.log(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.log(value))

    #square root
    @staticmethod
    def sqrt(value):
        if(type(value) is Rdm.Rdm):
            return value**(1.0/2.0)
        else:
            return rdmia.number(value**(1.0/2.0))

    #higher index root
    @staticmethod
    def hiRoot(value,index):
        if(type(value) is Rdm.Rdm):
            return value**(1.0/index)
        else:
            return rdmia.number(value**(1.0/index))

    #absolute value 
    @staticmethod
    def abs(value):
        if(type(value) is Rdm.Rdm):
            return RMath.sqrt(value**2.0)
        else:
            return abs(value)

    #sine function by sin² + cos² = 1
    @staticmethod
    def sin(value):
        #return rdmia.number(math.sin(RMath.degToRad(value)))
        if (type(value) is Rdm.Rdm):
            lower = math.sin(value.lower())
            upper = math.sin(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.sin(value))

    #cosine
    @staticmethod
    def cos(value):
        if (type(value) is Rdm.Rdm):
            lower = math.cos(value.lower())
            upper = math.cos(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.cos(value))

    #tangent
    @staticmethod
    def tan(value):
        if (type(value) is Rdm.Rdm):
            lower = math.tan(value.lower())
            upper = math.tan(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.tan(value))

    #secant
    @staticmethod
    def sec(value):
        if (type(value) is Rdm.Rdm):
            return 1.0/RMath.cos(value)
        else:
            return rdmia.number(math.sin(value))

    #cosecant
    @staticmethod
    def csc(value):
        if (type(value) is Rdm.Rdm):
            return 1.0/RMath.sin(value)
        else:
            return rdmia.number(1.0/math.sin(value))

    #cotangent
    @staticmethod
    def cot(value):
        if (type(value) is Rdm.Rdm):
            return RMath.cos(value)/RMath.sin(value)
        else:
            return rdmia.number(math.cos(value)/math.sin(value))

    #hyperbolic sine
    @staticmethod
    def sinh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.sinh(value.lower())
            upper = math.sinh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.sinh(value))

    #hyperbolic cosine
    @staticmethod
    def cosh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.cosh(value.lower())
            upper = math.cosh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.cosh(value))

    #hyperbolic tangent
    @staticmethod
    def tanh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.tanh(value.lower())
            upper = math.tanh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.tanh(value))
        
    #hyperbolic secant
    @staticmethod
    def sech(value):
        if (type(value) is Rdm.Rdm):
            return 1.0/RMath.cosh(value)
        else:
            return rdmia.number(1.0/math.cosh(value))

    #hyperbolic cosecant
    @staticmethod
    def csch(value):
        if (type(value) is Rdm.Rdm):
            return 1.0/RMath.sinh(value)
        else:
            return rdmia.number(1.0/math.sinh(value))

    #hyperbolic cotangent
    @staticmethod
    def coth(value):
        if (type(value) is Rdm.Rdm):
            return RMath.cosh(value)/RMath.sinh(value)
        else:
            return rdmia.number(math.cosh(value)/math.sinh(value))
    
    #inverse sine
    @staticmethod
    def asin(value):
        if (type(value) is Rdm.Rdm):
            lower = math.asin(value.lower())
            upper = math.asin(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.asin(value))

    #inverse cosine
    @staticmethod
    def acos(value):
        if (type(value) is Rdm.Rdm):
            lower = math.acos(value.lower())
            upper = math.acos(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.acos(value))

    #inverse tangent
    @staticmethod
    def atan(value):
        if (type(value) is Rdm.Rdm):
            lower = math.atan(value.lower())
            upper = math.atan(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.atan(value))

    #inverse hyperbolic sine
    @staticmethod
    def asinh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.asinh(value.lower())
            upper = math.asinh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.asinh(value))

    #inverse hyperbolic cosine
    @staticmethod
    def acosh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.acosh(value.lower())
            upper = math.acosh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.acosh(value))

    #inverse hyperbolic tangent
    @staticmethod
    def atanh(value):
        if (type(value) is Rdm.Rdm):
            lower = math.atanh(value.lower())
            upper = math.atanh(value.upper())
            return rdmia.number(lower,upper)
        else:
            return rdmia.number(math.atanh(value))