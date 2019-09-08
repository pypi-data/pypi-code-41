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
import numpy as np

#Calculates Relative Error

__all__ = ["QualitativeMetrics"]

class QualitativeMetrics(object):

    @staticmethod
    def relativeError(xInt,xReal):
        try:
            r = abs((xReal - QualitativeMetrics.centerI(xInt))/xReal)
            error = (QualitativeMetrics.diameter(xInt))/(2*xInt.lower)
        except:
            r = np.nan
            error =  np.nan
        return r,error

    @staticmethod
    def absoluteError(xInt,xReal):
        try:
            r = abs((xReal - QualitativeMetrics.centerI(xInt))/xReal)
            error = (QualitativeMetrics.diameter(xInt)/2)
        except:
            r =  np.nan
            error = np.nan
        return r,error

    #Calculates interval diameter
    @staticmethod
    def diameter(xInt):
        return xInt.upper - xInt.lower


    @staticmethod
    def centerI(xInt):
        return (xInt.lower + xInt.upper)/2.0

