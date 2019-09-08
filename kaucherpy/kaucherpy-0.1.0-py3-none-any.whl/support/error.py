# errors.py
#
# Copyright 2008 Rafael Menezes Barreto <rmb3@cin.ufpe.br,
# rafaelbarreto87@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


"""Error classes module

All error classes used in the IntPy package are centralized here.

It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto
<rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy package and
it's free software.
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
            IntervalError.__init__(self,"Operation not defined for Kaucher Interval, please check the right data")


class UndefinedValueIntervalError(IntervalError):
    def __init__(self,msg=None):
        if msg is None:
            IntervalError.__init__(self,"The interval not be empty.")
        else:
            IntervalError.__init__(self, msg)