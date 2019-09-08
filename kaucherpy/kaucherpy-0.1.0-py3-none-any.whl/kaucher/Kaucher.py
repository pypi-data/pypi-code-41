import numpy as np
import sys

from kaucherpy.core.Round import *
from kaucherpy.support.error import IntervalError
from kaucherpy.support.error import TypeIntervalError
from kaucherpy.support.error import UndefinedValueIntervalError
from kaucherpy.support.error import IntervalDivisionByZero 

__all__ = [
    "Kaucher"
]

class Kaucher(object):
    
    def __init__(self,lower=None,upper=None):
        
        '''if(upper == None and lower == None):
            self.upper = np.nan
            self.lower = np.nan
            self.isEmpty = True
        
        elif(upper is None):
            self.isEmpty = False
            self.lower = np.float64(lower)
            self.upper = np.float64(lower)
        else:
            self.isEmpty = False
            self.lower = np.float64(lower)
            self.upper = np.float64(upper)'''

        self.__set_limits(lower,upper)


    #IMPLEMENTAR PARA GANTIR VALORES NUMERICOS PARA KAUCHER
    def __set_limits(self,lower=None,upper=None):
        attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
        #Testing if lower is a numeric value
        if(not lower is None):
            self.isEmpty = False
            if(all(hasattr(lower, attr) for attr in attrs)):
                self.lower = np.float64(lower)
                self.upper = np.float64(lower)
            else:
                raise TypeIntervalError()
        else:
            self.lower = np.nan
            self.upper = np.nan

        if(not upper is None):
            self.isEmpty = False
            if(all(hasattr(upper, attr) for attr in attrs)):
                self.upper = np.float64(upper)
            else:
                raise TypeIntervalError()

    @property
    def lower(self):
        return self.__lower

    @property
    def upper(self):
        return self.__upper

    @property
    def isEmpty(self):
        return self.__isEmpty

    @isEmpty.setter
    def isEmpty(self,value):
        self.__isEmpty = value


    @lower.setter
    def lower(self,value):
        self.__lower = np.float64(value)
        self.__isEmpty = False
    
    @upper.setter
    def upper(self,value):
        self.__upper = np.float64(value)
        self.__isEmpty = False


    def __str__(self):
        return "["+str(self.lower)+" , "+str(self.upper)+"]"

    def __repr__(self):
        return "[%r, %r]" % (self.lower, self.upper)

    def __getitem__(self):
        return np.array([self.lower,self.upper])

    def __add__(self,other):
        other = self.__checkValue(other)

        Round.set_down_rounding()
        lower = self.lower+other.lower
        Round.set_up_rounding()
        Round.get_rounding()
        upper = self.upper+other.upper
        Round.set_normal_rounding()
        return Kaucher(lower,upper)



    def __sub__(self,other):
        other = self.__checkValue(other)

        Round.set_down_rounding()
        lower = self.lower-other.upper
        Round.set_up_rounding()
        upper = self.upper-other.lower
        Round.set_normal_rounding()

        return Kaucher(lower,upper)

    def __mul__(self,other):
        other = self.__checkValue(other)
        lower = np.float64(0)
        upper = np.float64(0)
        if(self.lower <= np.float64(0) and self.upper <= np.float64(0)):
            if(other.lower <= np.float64(0) and other.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = self.upper*other.upper
                Round.set_up_rounding()
                upper = self.lower*other.lower
                Round.set_normal_rounding()

            elif(other.lower < np.float64(0) < other.upper):
                Round.set_down_rounding()
                lower = self.lower*other.upper
                Round.set_up_rounding()
                upper = self.lower*other.lower
                Round.set_normal_rounding()

            elif(other.lower >= np.float64(0) and other.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = self.lower*other.upper
                Round.set_up_rounding()
                upper = self.upper*other.lower
                Round.set_normal_rounding()

            elif(other.upper < 0 < other.lower):
                Round.set_down_rounding()
                lower = self.upper*other.upper
                Round.set_up_rounding()
                upper = self.upper*other.lower
                Round.set_normal_rounding()

        elif(self.lower < np.float64(0) < self.upper):
            if(other.lower <= np.float64(0) and other.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = self.upper*other.lower
                Round.set_up_rounding()
                upper = self.lower*other.lower
                Round.set_normal_rounding()

            elif(other.lower < np.float64(0) < other.upper):
                Round.set_down_rounding()
                lower = min(self.lower*other.upper,self.upper*other.lower)
                Round.set_up_rounding()
                upper = max(self.lower*other.lower,self.upper*other.upper)
                Round.set_normal_rounding()

            elif(other.lower >= np.float64(0) and other.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = self.lower*other.upper
                Round.set_up_rounding()
                upper = self.upper*other.upper
                Round.set_normal_rounding()

            elif(other.upper < 0 < other.lower):
                lower = np.float64(0)
                upper = np.float64(0)

        elif(self.lower >= np.float64(0) and self.upper >= np.float64(0)):
            if(other.lower <= np.float64(0) and other.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = self.upper*other.lower
                Round.set_up_rounding()
                upper = self.lower*other.upper
                Round.set_normal_rounding()

            elif(other.lower < np.float64(0) < other.upper):
                Round.set_down_rounding()
                lower = self.upper*other.lower
                Round.set_up_rounding()
                upper = self.upper*other.upper
                Round.set_normal_rounding()

            elif(other.lower >= np.float64(0) and other.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = self.lower*other.lower
                Round.set_up_rounding()
                upper = self.upper*other.upper
                Round.set_normal_rounding()

            elif(other.upper < 0 < other.lower):
                Round.set_down_rounding()
                lower = self.lower*other.lower
                Round.set_up_rounding()
                upper = self.lower*other.upper
                Round.set_normal_rounding()

        elif(self.upper < 0 < self.lower):
            if(other.lower <= np.float64(0) and other.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = self.upper*other.upper
                Round.set_up_rounding()
                upper = self.lower*other.upper
                Round.set_normal_rounding()

            elif(other.lower < np.float64(0) < other.upper):
                lower = np.float64(0)
                upper = np.float64(0)
            elif(other.lower >= np.float64(0) and other.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = self.lower*other.lower
                Round.set_up_rounding()
                upper = self.upper*other.lower
                Round.set_normal_rounding()

            elif(other.upper < 0 < other.lower):
                Round.set_down_rounding()
                lower = max(self.lower*other.lower,self.upper*other.upper)
                Round.set_up_rounding()
                upper = min(self.lower*other.upper,self.upper*other.lower)
                Round.set_normal_rounding()

        return Kaucher(lower,upper)


    def __truediv__(self,other):
        other = self.__checkValue(other)
        if(other.lower*other.upper <= 0):
            raise IntervalDivisionByZero()
        else:
            Round.set_down_rounding()
            lower = self.lower/other.upper
            Round.set_up_rounding()
            upper = self.upper/other.lower
            Round.set_normal_rounding()
            return Kaucher(lower,upper)

    def __rtruediv__(self,other):
        other = self.__checkValue(other)
        if(self.lower*self.upper <= 0):
            raise IntervalDivisionByZero()
        else:
            Round.set_down_rounding()
            lower = other.lower/self.upper
            Round.set_up_rounding()
            upper = other.upper/self.lower
            Round.set_normal_rounding()
            return Kaucher(lower,upper)

    def __div__(self,other):
        other = self.__checkValue(other)
        if(other.lower*other.upper <= 0):
            raise IntervalDivisionByZero()
        else:
            Round.set_down_rounding()
            lower = self.lower/other.upper
            Round.set_up_rounding()
            upper = self.upper/other.lower
            Round.set_normal_rounding()
            return Kaucher(lower,upper)



    def __or__(self, other):
        other = self.__checkValue(other)
        return Kaucher(max(self.lower,other.lower),min(self.upper,other.upper))

    def __and__(self,other):
        other = self.__checkValue(other)
        return Kaucher(min(self.lower,other.lower),max(self.upper,other.upper))

    def __invert__(self):
        return Kaucher(self.upper,self.lower)


    def __neg__(self):
        return Kaucher(-self.upper,-self.lower)

    def __pow__(self,other):
        if(type(other) is Kaucher):
            lower = min(self.lower**other.lower,self.lower**other.upper,self.upper**other.lower,self.upper**other.upper)
            upper = max(self.lower**other.lower,self.lower**other.upper,self.upper**other.lower,self.upper**other.upper)
            return Kaucher(lower,upper)
        else:
            return Kaucher(self.lower**other,self.upper**other)

    def __contains__(self,other):
        if(type(other) is not Kaucher):
            if(self.lower <= other and self.upper >= other):
                return True
            else:
                return False
        else:
            if((other.lower >= self.lower) and (self.upper>=other.upper)):
                return True
            else:
                return False

    def __eq__(self,other):
        other = self.__checkValue(other)
        if((other.lower == self.lower) and (other.upper == self.upper)):
            return True
        else:
            return False

    def __lt__(self,other):
        other = self.__checkValue(other)
        if((self.lower < other.lower) and (self.upper < other.upper)):
            return True
        else:
            return False

    def __le__(self,other):
        other = self.__checkValue(other)
        if((self.lower <= other.lower) and (self.upper <= other.upper)):
            return True
        else:
            return False

    def __gt__(self,other):
        other = self.__checkValue(other)
        if((self.lower > other.lower) and (self.upper > other.upper)):
            return True
        else:
            return False

    def __ge__(self,other):
        other = self.__checkValue(other)
        if((self.lower >= other.lower) and (self.upper >= other.upper)):
            return True
        else:
            return False


    def __checkValue(self,other):
        if(type(other) is not Kaucher):
            other = Kaucher(other)
        self.__validateDefinedValue(other)
        return other

    def __validateDefinedValue(self,other):
        if(other.isEmpty or self.isEmpty):
            raise UndefinedValueIntervalError("The interval are empty, this a invalid operation")   


    def __radd__(self,other):
        other = self.__checkValue(other)

        Round.set_down_rounding()
        lower = other.lower+self.lower
        Round.set_up_rounding()
        Round.get_rounding()
        upper = other.upper+self.upper
        Round.set_normal_rounding()
        return Kaucher(lower,upper)

    def __rsub__(self,other):
        other = self.__checkValue(other)

        Round.set_down_rounding()
        lower = other.lower-self.upper
        Round.set_up_rounding()
        upper = other.upper-self.lower
        Round.set_normal_rounding()

        return Kaucher(lower,upper)

    def __rmul__(self,other):
        other = self.__checkValue(other)
        lower = np.float64(0)
        upper = np.float64(0)
        if(other.lower <= np.float64(0) and other.upper <= np.float64(0)):
            if(self.lower <= np.float64(0) and self.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = other.upper*self.upper
                Round.set_up_rounding()
                upper = other.lower*self.lower
                Round.set_normal_rounding()

            elif(self.lower < np.float64(0) < self.upper):
                Round.set_down_rounding()
                lower = other.lower*self.upper
                Round.set_up_rounding()
                upper = other.lower*self.lower
                Round.set_normal_rounding()

            elif(self.lower >= np.float64(0) and self.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = self.lower*other.upper
                Round.set_up_rounding()
                upper = self.upper*other.lower
                Round.set_normal_rounding()

            elif(self.upper < 0 < self.lower):
                Round.set_down_rounding()
                lower = self.upper*other.upper
                Round.set_up_rounding()
                upper = self.upper*other.lower
                Round.set_normal_rounding()

        elif(other.lower < np.float64(0) < other.upper):
            if(self.lower <= np.float64(0) and self.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = other.upper*self.lower
                Round.set_up_rounding()
                upper = other.lower*self.lower
                Round.set_normal_rounding()

            elif(self.lower < np.float64(0) < self.upper):
                Round.set_down_rounding()
                lower = min(other.lower*self.upper,other.upper*self.lower)
                Round.set_up_rounding()
                upper = max(other.lower*self.lower,other.upper*self.upper)
                Round.set_normal_rounding()

            elif(self.lower >= np.float64(0) and self.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = other.lower*self.upper
                Round.set_up_rounding()
                upper = other.upper*self.upper
                Round.set_normal_rounding()

            elif(self.upper < 0 < self.lower):
                lower = np.float64(0)
                upper = np.float64(0)

        elif(other.lower >= np.float64(0) and other.upper >= np.float64(0)):
            if(self.lower <= np.float64(0) and self.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = other.upper*self.lower
                Round.set_up_rounding()
                upper = other.lower*self.upper
                Round.set_normal_rounding()

            elif(self.lower < np.float64(0) < self.upper):
                Round.set_down_rounding()
                lower = other.upper*self.lower
                Round.set_up_rounding()
                upper = other.upper*self.upper
                Round.set_normal_rounding()

            elif(self.lower >= np.float64(0) and self.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = other.lower*self.lower
                Round.set_up_rounding()
                upper = other.upper*self.upper
                Round.set_normal_rounding()

            elif(self.upper < 0 < self.lower):
                Round.set_down_rounding()
                lower = other.lower*self.lower
                Round.set_up_rounding()
                upper = other.lower*self.upper
                Round.set_normal_rounding()

        elif(other.upper < 0 < other.lower):
            if(self.lower <= np.float64(0) and self.upper <= np.float64(0)):
                Round.set_down_rounding()
                lower = other.upper*self.upper
                Round.set_up_rounding()
                upper = other.lower*self.upper
                Round.set_normal_rounding()

            elif(self.lower < np.float64(0) < self.upper):
                lower = np.float64(0)
                upper = np.float64(0)
            elif(self.lower >= np.float64(0) and self.upper >= np.float64(0)):
                Round.set_down_rounding()
                lower = other.lower*self.lower
                Round.set_up_rounding()
                upper = other.upper*self.lower
                Round.set_normal_rounding()

            elif(self.upper < 0 < self.lower):
                Round.set_down_rounding()
                lower = max(other.lower*self.lower,other.upper*self.upper)
                Round.set_up_rounding()
                upper = min(other.lower*self.upper,other.upper*self.lower)
                Round.set_normal_rounding()

        return Kaucher(lower,upper)

    def __rdiv__(self,other):
        other = self.__checkValue(other)
        if(self.lower*self.upper <= 0):
            raise IntervalDivisionByZero()
        else:
            Round.set_down_rounding()
            lower = other.lower/self.upper
            Round.set_up_rounding()
            upper = other.upper/self.lower
            Round.set_normal_rounding()
            return Kaucher(lower,upper)

    __ror__ = __or__
    __rand__ = __and__
    __rpow__ = __pow__


#a = Kaucher(2.0,3.0)
#b = Kaucher(2.5)
#d = Kaucher(5.0)
#c = 2.5
#print d > b
#print b in a
#print (c in a)
#print d in a
#print (a==b)
#print (a==a)
#print (b==2.5)
#print ~a
#print -a
#print (2.5 + b)
#print (a or b)