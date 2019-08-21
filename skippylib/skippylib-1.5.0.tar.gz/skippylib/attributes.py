# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from .abstracts import AbstractSkippyAttribute
from .features import RampFeature, RawDataFeature, ArrayDataInterpreterFeature
from numpy import bool, int16, uint16, int32, uint32, int64, uint64
import PyTango
from time import time, sleep
import traceback

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class SkippyAttribute(AbstractSkippyAttribute):

    _switchObj = None
    _switchName = None

    def __init__(self, id, type, dim, parent=None, withRawData=False,
                 *args, **kwargs):
        super(SkippyAttribute, self).__init__(*args, **kwargs)
        self._id = id
        self._type = type
        self._dim = dim
        self._parent = parent
        if withRawData:
            self._raw = RawDataFeature(name="rawdata", parent=self)
        else:
            self._raw = None
        if self.dim == 1:
            if not hasattr(self, '_raw') or not self._raw:
                self._raw = RawDataFeature(name="rawdata", parent=self)
            self._array_interpreter = \
                ArrayDataInterpreterFeature(
                    name="array", parent=self, rawObj=self._raw)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def timestampsThreshold(self):
        if self._parent is not None and \
                hasattr(self._parent, 'timestampsThreshold'):
            return self._parent.timestampsThreshold
        return 0

    @property
    def dim(self):
        return self._dim

    def isWritable(self):
        return False

    def isRampeable(self):
        return False

    def hasWriteValues(self):
        return False

    def hasRawData(self):
        if self._raw is None:
            return False
        return True

    def hasArrayInterpreter(self):
        if self._array_interpreter is None:
            return False
        return True

    def hasSwitchAttribute(self):
        return self._switchName is not None

    def _buildrepr_(self, attributes):
        def lambda2str(func):
            try:
                self.debug_stream(
                    "constants: {0!r}".format(func.func_code.co_consts))
            except Exception as exc:
                self.error_stream(
                    "for attr {}, couldn't print the {} lambda consts "
                    "{}".format(self.name, key, func.func_code))
            if isinstance(func.__code__.co_consts[1], str):
                return func.__code__.co_consts[1]
            elif str(type(func.__code__.co_consts[1])) == "<type 'code'>":
                return func.__code__.co_consts[1].co_consts[1]
            else:
                self.error_stream(
                    "unknown how to represent {x}"
                    "".format(x=func.__code__.co_consts))

        repr = "%s (%s):\n" % (self.name, self.__class__.__name__)
        for key in attributes:
            if hasattr(self, key):
                attr = getattr(self, key)
                if attr is None:
                    # FIXME: when is None, it can be omitted
                    # but is nice to see it while in development
                    # (except for writable and wvalue that means
                    # that it wasn't wrote before
                    repr += "\t%s: None\n" % (key)
                elif isinstance(attr, list) and len(attr) == 0:
                    repr += "\t%s: []\n" % (key)
                elif isinstance(attr, str):
                    repr += "\t%s: %r\n" % (key, attr)
                elif hasattr(attr, '__call__'):  # lambda, for example
                    if attr.func_name == '<lambda>':
                        cmd = lambda2str(attr)
                        repr += "\t%s: %r\n" % (key, cmd)
                    else:
                        self.warn_stream(
                            "unknown callable element {k}".format(k=key))
                else:
                    repr += "\t%s: %s\n" % (key, attr)
            else:
                self.debug_stream("In _buildrepr_() doesn't have %s" % (key))
        return repr

# FIXME: it doesn't work as expected
#     def _buildRawFunctionality(self):
#         self._raw = RawDataFeature("rawdata", self)
#         self._makeRawDataProperties()
#
#     def _makeRawDataProperties(self):
#         setattr(self, 'lastReadRaw', self._makeLastReadRawProperty())
#
#     def _makeLastReadRawProperty(self):
#         def getter(self):
#             return self._raw.lastReadRaw
#
#         def setter(self, value):
#             self._raw.lastReadRaw = value
#
#         return property(getter, setter)

    def getSwitchAttrObj(self):
        if self._switchName is not None and self._switchObj is None:
            self._linkSwitchAttr()
        return self._switchObj

    def setSwitchAttrName(self, attrName):
        if self._parent is not None:
            if attrName == self._switchName:
                self.warn_stream(
                    "{0} changing switch attribute from {1} to {2}".format(
                        self.name, self._switchName, attrName))
            self._switchName = attrName
            self._linkSwitchAttr()

    def _linkSwitchAttr(self):
        if self._switchName in self._parent._attributes:
            self._switchObj = self._parent._attributes[self._switchName]
            self.info_stream("Link {0} with {1} switch attribute".format(
                self.name, self._switchObj.name))

    def interpretBoolean(self, value):
        if isinstance(value, str):
            value = value.lower()
        if value in [False, 0, '0', 'false', 'off']:
            return False
        elif value in [True, 1, '1', 'true', 'on']:
            return True
        return False

    @property
    def arrayInterpreter(self):
        return self._array_interpreter

    def interpretArray(self, dtype):
        if self._array_interpreter:
            return self._array_interpreter.interpretArray(dtype)


class SkippyReadAttribute(SkippyAttribute):
    def __init__(self, readCmd, readFormula=None,
                 *args, **kwargs):
        super(SkippyReadAttribute, self).__init__(*args, **kwargs)
        self._readCmd = readCmd
        self._readFormula = readFormula
        self._lastReadValue = None
        self._timestamp = None
        self._quality = PyTango.AttrQuality.ATTR_INVALID

    def __str__(self):
        return "%s (%s) [%s, %s, %s]" % (self.name, self.__class__.__name__,
                                         self.rvalue, self.timestamp,
                                         self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'timestamp', 'quality', 'type',
                                 'dim', 'readCmd', 'readFormula'])

    @property
    def readCmd(self):
        return self._readCmd

    def _read(self, query):
        if self._parent is not None and hasattr(self._parent, 'Read'):
            return self._parent.Read(query)

    @property
    def readFormula(self):
        return self._readFormula

    @property
    def rvalue(self):
        if self.getSwitchAttrObj() is not None and \
                self.getSwitchAttrObj().rvalue is False:
            self.info_stream(
                "Inhibit {0} reading because the {1} switch attribute is OFF"
                "".format(self.name, self._switchName))
            self.quality = PyTango.AttrQuality.ATTR_INVALID
            self._lastReadValue = None
            return
        if self._timestamp is not None and \
                time() - self._timestamp < self.timestampsThreshold:
            return self._lastReadValue
        newReadValue = self._read(self.readCmd)
        if newReadValue is None:
            self.quality = PyTango.AttrQuality.ATTR_INVALID
            return
        elif isinstance(newReadValue, str) and len(newReadValue) == 0:
            self.debug_stream("Uninterpretable data received")
            self.quality = PyTango.AttrQuality.ATTR_INVALID
            return
        t = time()
        if self._readFormula:
            self.debug_stream("Evaluating %r with VALUE=%r"
                              % (self._readFormula, newReadValue))
            try:
                formula = self._readFormula.replace("VALUE", "%r"
                                                    % newReadValue)
                self.debug_stream("eval(%r)" % (formula))
                return eval(formula)
            except Exception as e:
                self.warn_stream("Exception evaluating formula: %s" % (e))
        else:
            try:
                # FIXME: split in submethods between data types and dimesions
                #  this segment of code is getting to long and complex
                if self.type in [PyTango.DevDouble, PyTango.DevFloat]:
                    if self.dim == 0:
                        self._lastReadValue = float(newReadValue)
                    elif self.dim == 1:
                        self._raw.lastReadRaw = newReadValue
                        self._lastReadValue = self.interpretArray(dtype=float)
                    else:
                        raise BufferError("Unsuported multidimensional data")
                elif self.type in [PyTango.DevShort, PyTango.DevUShort,
                                   PyTango.DevInt, PyTango.DevLong,
                                   PyTango.DevULong, PyTango.DevLong64,
                                   PyTango.DevULong64]:
                    if self.dim == 0:
                        if hasattr(newReadValue, 'count') and \
                                newReadValue.count('.') == 1:
                            self._lastReadValue = int(float(newReadValue))
                        else:
                            self._lastReadValue = int(newReadValue)
                    elif self.dim == 1:
                        self._raw.lastReadRaw = newReadValue
                        dtype = {PyTango.DevShort: int16,
                                 PyTango.DevUShort: uint16,
                                 PyTango.DevInt: int,
                                 PyTango.DevLong: int32,
                                 PyTango.DevULong: uint32,
                                 PyTango.DevLong64: int64,
                                 PyTango.DevULong64: uint64,
                                 }[self.type]
                        self._lastReadValue = self.interpretArray(dtype=dtype)
                    else:
                        raise BufferError("Unsupported multidimensional data")
                elif self.type in [PyTango.DevBoolean]:
                    if self.dim == 0:
                        self._lastReadValue = self.interpretBoolean(
                            newReadValue)
                    elif self.dim == 1:
                        self._raw.lastReadRaw = newReadValue
                        self._lastReadValue = self.interpretArray(dtype=bool)
                    else:
                        raise BufferError("Unsupported multidimensional data")
                elif self.type in [PyTango.DevString]:
                    if self.dim == 0:
                        self._lastReadValue = newReadValue
                    elif self.dim == 1:
                        raise BufferError("Unsupported array data")
                    else:
                        raise BufferError("Unsupported multidimensional data")
                else:
                    self.warn_stream(
                        "type {x} not in the list of managed types"
                        "".format(x=self.type))
            except Exception as e:
                self.error_stream("Cannot convert string to %s (dim %d)"
                                  % (self.type, self.dim))
                self.debug_stream("Exception: %s" % (e))
                traceback.print_exc()
                return None
        self.timestamp = t
        if self._lastReadValue is not None:
            self.quality = PyTango.AttrQuality.ATTR_VALID
            return self._lastReadValue
        self.quality = PyTango.AttrQuality.ATTR_INVALID

    @property
    def lastReadValue(self):
        self.debug_stream("Requested %s.lastReadValue %s"
                          % (self.name, self._lastReadValue))
        return self._lastReadValue

    @lastReadValue.setter
    def lastReadValue(self, value):
        self.debug_stream("New %s.lastReadValue received %s"
                          % (self.name, value))
        self._lastReadValue = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        self._quality = value


class SkippyReadWriteAttribute(SkippyReadAttribute):
    # FIXME: this class is getting dirty due to the ramp: too many specific
    #        methods when the ramp should be encapsulated apart.
    def __init__(self, writeCmd=None, writeFormula=None, rampeable=False,
                 writeValues=None, delayAfterWrite=0.0, *args, **kwargs):
        super(SkippyReadWriteAttribute, self).__init__(*args, **kwargs)
        self._writeCmd = writeCmd
        self._writeFormula = writeFormula
        self._delayAfterWrite = delayAfterWrite
        self._lastWriteValue = None
        self._ramp = None
        if rampeable:
            self.makeRampeable()
        self._writeValues = writeValues

    def __str__(self):
        return "%s (%s) [(%s, %s), %s, %s]" % (self.name,
                                               self.__class__.__name__,
                                               self.rvalue, self.wvalue,
                                               self.timestamp, self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'wvalue', 'timestamp', 'quality',
                                 'type', 'dim', 'readCmd', 'readFormula',
                                 'writeCmd',
                                 # 'writeFormula'
                                 ])

    def isWritable(self):
        return True

    def hasWriteValues(self):
        return self._writeValues is not None

    @property
    def writeCmd(self):
        return self._writeCmd

    def _write(self, cmd):
        if self._parent is not None and\
                hasattr(self._parent, 'Write'):
            self._parent.Write(cmd)
            if self._delayAfterWrite > 0.0:
                self.debug_stream(
                    "{name} forces a delay after write of {v:f} seconds"
                    "".format(name=self.name, v=self._delayAfterWrite))
                sleep(self._delayAfterWrite)

    @property
    def writeFormula(self):
        return self._writeFormula

    @property
    def delayAfterWrite(self):
        return self._delayAfterWrite

    @property
    def wvalue(self):
        return self._lastWriteValue

    @property
    def lastWriteValue(self):
        return self._lastWriteValue

    @lastWriteValue.setter
    def lastWriteValue(self, value):
        self.debug_stream("New %s.lastWriteValue received %s"
                  % (self.name, value))
        self._lastWriteValue = value

    def isRampeable(self):
        if self._ramp is None:
            return False
        return True

    def makeRampeable(self):
        if self._ramp is None:
            self._ramp = RampFeature(name="ramp", parent=self)

    def getRampObj(self):
        return self._ramp

    @property
    def writeValues(self):
        return self._writeValues

    def setWriteValues(self, writeValues):
        self._writeValues = writeValues
