from ..core import Rdmia as rdmia
from ..core import Rdm
import numpy as np

__all__ = ["QualitativeMetrics"]

class QualitativeMetrics(object):

    #Calculates relative error of the interval
    @staticmethod
    def relativeError(xInt,xReal):
        try:
            r = abs((xReal - QualitativeMetrics.midpoint(xInt))/xReal)
            error = (QualitativeMetrics.diameter(xInt))/(2*xInt.lower())
        except:
            r = np.nan
            error =  np.nan
        return r,error

    #Calculates absolute error of the interval
    @staticmethod
    def absoluteError(xInt,xReal):
        try:
            r = abs((xReal - QualitativeMetrics.midpoint(xInt))/xReal)
            error = (QualitativeMetrics.diameter(xInt)/2)
        except:
            r =  np.nan
            error = np.nan
        return r,error

    #Calculates interval diameter
    @staticmethod
    def diameter(xInt):
        return xInt.upper() - xInt.lower()

    #Calculates midpoint from the interval
    @staticmethod
    def midpoint(xInt):
        return (xInt.lower() + xInt.upper())/2.0

    #Calculates radius from the interval
    @staticmethod
    def radius(xInt):
        return (xInt.upper() - xInt.lower())/2.0

