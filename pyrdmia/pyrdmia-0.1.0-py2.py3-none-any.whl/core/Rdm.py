# PyRDMIA Python Library 2018
# RDM-IA implementation by
# Dirceu Maraschin Jr
# Lucas Tortelli

'''
This file contains the main class responsible for creating 
the RDM type and all standard operations and complex operations 
defined following the original concepts of RDM arithmetic.
'''

import numpy as np
import sys
from ..support.error import IntervalError
from ..support.error import TypeIntervalError
from ..support.error import UndefinedValueIntervalError
from ..support.error import IntervalDivisionByZero
from threading import Thread
import threading

__name__ = "Rdm"

class Rdm(object):
    _lower = 0.0 
    _upper = 0.0 
    _alpha = 0.0 
    f = None

    def __init__(self,x,y,precision=0.1):
        self._alpha = precision
        self._lower = np.float64(x)
        self._upper = np.float64(x) if y is None  else np.float64(y)
        #self.__isEmpty = True
        self._f = lambda alpha: self._lower + alpha*(self._upper - self._lower) 

    def lower(self):
        return self._lower

    def upper(self):
        return self._upper

    def __checkValue(self,other):
        if(type(other) is not Rdm):
            other = Rdm(other,None)
        return other

    #def isEmpty(self):
    #    return self.__isEmpty

    def __str__(self):
        return "["+str(self._lower)+", "+str(self._upper)+"]"

    def __repr__(self):
        return "[%r, %r]" % (self._lower, self._upper)

    def __getitem__(self):
        return np.array([self._lower,self._upper])

    def __operation__(self,alpha_self,other,operation,r,values):
        if(operation == "ADD"):
            if(not r):    
                #add
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_self) + other._f(alpha_other))
            else:
                #radd
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) + self._f(alpha_self))

        elif(operation == "SUB"):
            if(not r):    
                #sub
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_self) - other._f(alpha_other))
            else:
                #rsub
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) - self._f(alpha_self))

        elif(operation == "MUL"):
            if(not r):    
                #mul
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_self) * other._f(alpha_other))
            else:
                #rmul
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) * self._f(alpha_self))

        elif(operation == "DIV"):
            if(not r):    
                #div
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_self) / other._f(alpha_other))
            else:
                #rdiv
                for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) / self._f(alpha_self))
        elif(operation == "POW"):
            for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                values.append(self._f(alpha_self) ** other._f(alpha_other))


    #Default operations since they are all or initially RDM numbers.
    def __add__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_other) + other._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"ADD",False,values)
        return Rdm(min(values),max(values))

    def __sub__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_other) - other._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"SUB",False,values)
        return Rdm(min(values),max(values))

    def __mul__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_other) * other._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"MUL",False,values)
        return Rdm(min(values),max(values))

    def __div__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(self._f(alpha_other) / other._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"DIV",False,values)
        return Rdm(min(values),max(values))

    #default operations given that possibly an initial number is not an RDM number
    def __radd__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) + self._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"ADD",True,values)
        return Rdm(min(values),max(values))

    def __rsub__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) - self._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"SUB",True,values)
        return Rdm(min(values),max(values))

    def __rmul__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) * self._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"MUL",True,values)
        return Rdm(min(values),max(values))

    def __rdiv__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        if(id(other) == id(self)):
             for alpha_other in np.arange(0,(1+self._alpha),self._alpha):
                    values.append(other._f(alpha_other) / self._f(alpha_other))
        else:
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"DIV",True,values)
        return Rdm(min(values),max(values))

    #control
    '''
    def __checkValue(self,other):
        if(type(other) is not Rdm):
            other = Rdm(other)
        self.__validateDefinedValue(other)
        return other

    def __validateDefinedValue(self,other):
        if(other.isEmpty or self.isEmpty):
            raise UndefinedValueIntervalError("Invalid operation! The interval are empty.")
    '''
    
    #complementary and unary operations 
    #power operation
    def __pow__(self,other):
        other = self.__checkValue(other)
        values = []
        v = 0
        rdmOperation = []
        for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
            for alpha_self in np.arange(0,(1+self._alpha),self._alpha):
                self.__operation__(alpha_self,other,"POW",None,values)
        return Rdm(min(values),max(values))


    #union operator
    def __or__(self, other):
        other = self.__checkValue(other)
        return Rdm(min(self.lower(),other.lower()),max(self.upper(),other.upper()))
    
    #intersection operator
    def __and__(self,other):
        other = self.__checkValue(other)
        if (max(self.lower(),other.lower())) <= (min(self.upper(),other.upper())):
            return Rdm(max(self.lower(),other.lower()),min(self.upper(),other.upper()))
        else:
            raise TypeIntervalError("empty interval")
    '''
    before
    if (max(self.lower(),other.lower())) <= (min(self.upper(),other.upper())):
        raise UndefinedValueIntervalError("Invalid operation! Returns an improper interval.")
    else:
        return Rdm(min(self.upper(),other.upper()),max(self.lower(),other.lower()))
    '''

    #interval inversion
    def __invert__(self):
        return Rdm(self.upper(),self.lower())

    #interval deny
    def __neg__(self):
        return Rdm(-self.upper(),-self.lower())

    #equality test
    def __eq__(self,other):
        other = self.__checkValue(other)
        if((other.lower() == self.lower()) and (other.upper() == self.upper())):
            return True
        else:
            return False
    
    #inequality test
    def __neq__(self,other):
        other = self.__checkValue(other)
        if((other.lower() != self.lower()) and (other.upper() != self.upper())):
            return True
        else:
            return False

    def __iter__(self):
        raise TypeError

    #contains operator
    def __contains__(self,other):
        if(type(other) is not Rdm):
            if(self.lower() <= other and self.upper() >= other):
                return True
            else:
                return False
        else:
            if((other.lower() >= self.lower()) and (self.upper() >= other.upper())):
                return True
            else:
                return False

    #comparison operator "less than"
    def __lt__(self,other):
        other = self.__checkValue(other)
        if((self.lower() < other.lower()) and (self.upper() < other.upper())):
            return True
        else:
            return False

    #comparison operator "less or equal"
    def __le__(self,other):
        other = self.__checkValue(other)
        if((self.lower() <= other.lower()) and (self.upper() <= other.upper())):
            return True
        else:
            return False

    #comparison operator "greater than"
    def __gt__(self,other):
        other = self.__checkValue(other)
        if((self.lower() > other.lower()) and (self.upper() > other.upper())):
            return True
        else:
            return False

    #comparison operator "greater or equal"
    def __ge__(self,other):
        other = self.__checkValue(other)
        if((self.lower() >= other.lower()) and (self.upper() >= other.upper())):
            return True
        else:
            return False

    __truediv__ = __div__
    __rtruediv__ = __rdiv__
    __ror__ = __or__
    __rand__ = __and__
    __rpow__ = __pow__