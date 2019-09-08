# Copyright 2015 Aline Brum Loreto<aline.loreto@lower.ufpel.edu.br>, Alice Fonseca Finger <aliceffinger@gmail.com>, Mauricio Dorneles
# Caldeira Balboni<mdcbalboni@lower.ufpel.edu.br>,Lucas Mendes Tortelli <lmtortelli@lower.ufpel.edu.br>, Vinicius Signori Furlan<vsfurlan@.lower.ufpel.edu.br>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from kaucherpy import Kaucher
import math

__all__ = ["KMath"]

class KMath(object):
    
    E = Kaucher(2.718281828459045235360287)
    PI = Kaucher(math.pi)

    @staticmethod
    def degToRad(value):
        rad = (value/180)*KMath.PI
        if (type(rad) is Kaucher):
            return rad
        else:
            return Kaucher(rad)
        #abaixo: definição da função seno por sin² + cos² = 1

    @staticmethod
    def sin(value):
        r = 0
        r = KMath.sqrt(1 - (KMath.cos(value))**2)
        return r

    @staticmethod
    def cos(rad):
        n = KMath.degToRad(rad)
        c = 0
        r = 1
        while(c < 50):
            c += 1
            r += (((-1)**c)*(n**(2 * c)))/(math.factorial(2 * c))
        return r

    @staticmethod
    def exp(x):
        return KMath.E**x

    @staticmethod
    def sqrt(x):
        if(type(x) is Kaucher):
            return x**(1.0/2.0)
        else:
            return Kaucher(x**(1.0/2.0))

    @staticmethod
    def abs(x):
        return Kaucher(abs(x.lower),abs(x.upper))

'''
    def acos(x, rnd=0):
        pass

    def acosh(x, rnd=0):
        pass

    def asin(x, rnd=0):
        pass

    def asinh(x, rnd=0):
        pass

    def atan(x, rnd=0):
        pass

    def atanh(x, rnd=0):
        pass

    def cos(x, rnd=0):
        pass

    def cosh(x, rnd=0):
        pass

    def cot(x, rnd=0):
        pass

    def csc(x, rnd=0):
        pass

    def exp(x, rnd=0):
        pass

    def log(x, rnd=0, base=2):
        pass

    def pow(x, y, rnd=0):
        pass

    def sec(x, rnd=0):
        pass

    def sinh(x, rnd=0):
        pass

    def sqrt(x, rnd=0):
        pass

    def tan(x, rnd=0):
        pass

    def tanh(x, rnd=0):
        pass
'''