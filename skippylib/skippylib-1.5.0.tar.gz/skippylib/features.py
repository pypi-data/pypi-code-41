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

import numpy
from .abstracts import AbstractSkippyAttribute, AbstractSkippyFeature
from .dataformat import interpret_binary_format
from PyTango import DevState
import struct
from threading import Thread
from time import sleep

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class SkippyFeature(AbstractSkippyFeature):
    def __init__(self, parent, *args, **kwargs):
        super(SkippyFeature, self).__init__(*args, **kwargs)
        if parent is None:
            raise AssertionError("Functionality must have a parent")
        if not isinstance(parent, AbstractSkippyAttribute):
            raise AssertionError("Functionality parent must be an attribute "
                                 "object")
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)

    def _buildrepr_(self, attributes):
        repr = "%s:\n" % self
        for key in attributes:
            attr = getattr(self, key)
            if attr is None:
                repr += "\t%s: None\n" % (key)
            elif isinstance(attr, list) and len(attr) == 0:
                repr += "\t%s: []\n" % (key)
            elif isinstance(attr, str):
                repr += "\t%s: %r\n" % (key, attr)
            elif hasattr(attr, '__call__'):
                args = [0]*attr.__code__.co_argcount
                repr += "\t%s: %r\n" % (key, attr(*args))
            else:
                repr += "\t%s: %s\n" % (key, attr)
        return repr


class RampFeature(SkippyFeature):
    def __init__(self, *args, **kwargs):
        super(RampFeature, self).__init__(*args, **kwargs)
        self._rampStep = None
        self._rampStepSpeed = None
        self._rampThread = None
    # FIXME: this is only a ramping for float attributes, should also support
    #        integers.
    # FIXME: prevent from attributes with a set of write values to have a ramp.

    def __repr__(self):
        return self._buildrepr_(['rampStep', 'rampStepSpeep'])

    @property
    def rampStep(self):
        return self._rampStep

    @rampStep.setter
    def rampStep(self, value):
        if value is not None:
            self._rampStep = float(value)

    @property
    def rampStepSpeed(self):
        return self._rampStepSpeed

    @rampStepSpeed.setter
    def rampStepSpeed(self, value):
        if value is not None:
            self._rampStepSpeed = float(value)

    @property
    def rampThread(self):
        return self._rampThread

#     @rampThread.setter
#     def rampThread(self, value):
#         self._rampThread = value

    def isRamping(self):
        if self.rampThread is not None and self.rampThread.isAlive():
            return True
        return False

    def prepareRamping(self):
        try:
            thread = Thread(target=self._rampProcedure,
                            name="%s_ramp" % (self._parent.name))
            thread.setDaemon(True)
        except Exception as e:
            self.error_stream("Prepare ramp exception: %s" % (e))
            return False
        else:
            self._rampThread = thread
            return True

    def launchRamp(self):
        try:
            self._rampThread.start()
        except:
            return False
        else:
            return True

    def _rampProcedure(self):
        '''Important things of the ramp procedure:
           - before do the evaluation of the next step is always doing a new
             read of the destination value. If the user has changed the
             destination value, the ramp will continue to the newer place.
           - the step and the time on each step will also be using the latest.
             If the user changes the ramp during one, the newer configuration
             will be used from then on.
           - The last step can be smaller than configured if (and ony if) the
             distance is smaller than the step.
           - The state of the device will be preserved after the ramp, but
             modified to MOVING while is working the ramp.
             # FIXME: run condition if there are two ramps and the second
             ends later. The first will restore the state, when the second is
             working and when this seconds finish will restore a moving state!
           TODO: future improvements for ramps:
           - Current ramp is like an step scan. There are other ramps possible:
             - On each step move a percentage of the distance (like move 2/3th
               until close enough).
             - Acceleration - motion - deceleration.
        '''
        # prepare
        backup_state = self._get_state()
        self._change_state_status(newState=DevState.MOVING)
        orig_pos = self._parent.rvalue
        dest_pos = self._parent.wvalue
        self.info_stream("In _rampProcedure(): ramp will start from %g to %g"
                         % (orig_pos, dest_pos))
        while not orig_pos == dest_pos:
            diff = abs(orig_pos - dest_pos)
            if diff < self.rampStep:
                new_pos = dest_pos  # Last step
            # else, do one step in the correct direction
            elif orig_pos > dest_pos:
                new_pos = orig_pos - self.rampStep
            elif orig_pos < dest_pos:
                new_pos = orig_pos + self.rampStep
            attrWriteCmd = self._parent.writeCmd(new_pos)
            self.info_stream("In _rampProcedure() step from %f to %f sending: "
                             "%s" % (orig_pos, dest_pos, attrWriteCmd))
            self._write(attrWriteCmd)
            sleep(self.rampStepSpeed)
            # get newer values
            orig_pos = self._parent.rvalue
            dest_pos = self._parent.wvalue
        self.info_stream("In _rampProcedure(): finished the movement at %f"
                         % (dest_pos))
        # close
        self._change_state_status(newState=backup_state, rebuild=True)
        self._rampThread = None

    def _write(self, cmd):
        self._parent._write(cmd)


class RawDataFeature(SkippyFeature):
    def __init__(self, *args, **kwargs):
        super(RawDataFeature, self).__init__(*args, **kwargs)
        self._lastReadRaw = None

    def __repr__(self):
        return self._buildrepr_(['rawData'])

    @property
    def lastReadRaw(self):
        return self._lastReadRaw

    @lastReadRaw.setter
    def lastReadRaw(self, value):
        if len(value) > 100:
            answer_repr = "{0!r}(...){1!r}".format(
                value[:25], value[len(value)-25:])
        else:
            answer_repr = "{0!r}".format(value)
        self.debug_stream("set raw data: %s" % (answer_repr))
        self._lastReadRaw = value


DEFAULT_WAVEFORM_DATAFORMAT = 'WaveformDataFormat'
DEFAULT_WAVEFORM_ORIGIN = 'WaveformOrigin'
DEFAULT_WAVEFORM_INCREMENT = 'WaveformIncrement'

class ArrayDataInterpreterFeature(SkippyFeature):

    _dataFormatAttrName = None
    _dataFormatAttrObj = None

    _originAttrName = None
    _originAttrObj = None

    _incrementAttrName = None
    _incrementAttrObj = None

    def __init__(self, rawObj, format=None, origin=None, increment=None,
                 *args, **kwargs):
        super(ArrayDataInterpreterFeature, self).__init__(*args, **kwargs)
        self._rawObj = rawObj
        self.dataFormatAttr = format
        self.originAttr = origin
        self.incrementAttr = increment

    @property
    def rawObj(self):
        return self._rawObj

    def __getParentAttr(self, attrName):
        if self._parent is not None:
            attrObj = self._parent
            if attrObj._parent is not None:
                container = attrObj._parent
                if hasattr(container, 'attributes'):
                    attributes = getattr(container, 'attributes')
                    if attrName:
                        if attrName in attributes:
                            return attributes[attrName]
                        else:
                            self.debug_stream("%s not in attributes"
                                              % (attrName))
                else:
                    self.debug_stream("container of my SkippyAttribute "
                                      "doesn't support attributes")
            else:
                self.debug_stream("My SkippyAttribute doesn't have parent")
        else:
            self.debug_stream("This functionality doesn't have parent")

    @property
    def _dataFormat(self):
        attrObj = self.dataFormatAttr
        if attrObj is not None:
            value = attrObj.rvalue
            if value is not None:
                return value
        return ''

    @property
    def dataFormatAttr(self):
        if self._dataFormatAttrObj is None:
            if self._dataFormatAttrName is None:
                self._dataFormatAttrObj = self.__getParentAttr(
                    DEFAULT_WAVEFORM_DATAFORMAT)
            else:
                self._dataFormatAttrObj = self.__getParentAttr(
                    self._dataFormatAttrName)
        return self._dataFormatAttrObj

    @dataFormatAttr.setter
    def dataFormatAttr(self, attrName):
        if attrName is None:
            self._dataFormatAttrName = DEFAULT_WAVEFORM_DATAFORMAT
        else:
            self._dataFormatAttrName = attrName
        self._dataFormatAttrObj = self.__getParentAttr(
            self._dataFormatAttrName)

    @property
    def _origin(self):
        attrObj = self.originAttr
        if attrObj is not None:
            value = attrObj.rvalue
            if value is not None:
                return value
        return 0.0  # addition factor

    @property
    def originAttr(self):
        if self._originAttrObj is None:
            if self._originAttrName is None:
                self._originAttrObj = self.__getParentAttr(
                    DEFAULT_WAVEFORM_ORIGIN)
            else:
                self._originAttrObj = self.__getParentAttr(
                    self._originAttrName)
        return self._originAttrObj

    @originAttr.setter
    def originAttr(self, attrName):
        if attrName is None:
            self._originAttrName = DEFAULT_WAVEFORM_ORIGIN
        else:
            self._originAttrName = attrName
        self._originAttrObj = self.__getParentAttr(self._originAttrName)

    @property
    def _increment(self):
        attrObj = self.originAttr
        if attrObj is not None:
            value = attrObj.rvalue
            if value is not None:
                return value
        return 1.0  # multiplier factor

    @property
    def incrementAttr(self):
        if self._incrementAttrObj is None:
            if self._incrementAttrName is None:
                self._incrementAttrObj = self.__getParentAttr(
                    DEFAULT_WAVEFORM_INCREMENT)
            else:
                self._incrementAttrObj = self.__getParentAttr(
                    self._incrementAttrName)
        return self._incrementAttrObj

    @incrementAttr.setter
    def incrementAttr(self, attrName):
        if attrName is None:
            self._incrementAttrName = DEFAULT_WAVEFORM_INCREMENT
        else:
            self._incrementAttrName = attrName
        self._incrementAttrObj = self.__getParentAttr(self._incrementAttrName)

    def interpretArray(self, dtype):
        if self._rawObj is None or self._parent is None:
            raise AssertionError("It is necessary to have SkippyAttribute and "
                                 "RawDataFeature objects to interpret data")
        if dtype in [numpy.bool, numpy.int16, numpy.uint16, int,
                     numpy.int32, numpy.uint32, numpy.int64, numpy.uint64]:
            # FIXME: Binary data formats may only apply to floats
            #  Or perhaps also to numericals, but booleans may only have
            #  4 simbols (0, false, 1, true) in ascii and bit arrays in binary
            dataFormat = 'ASC'
        else:
            dataFormat = self._dataFormat
        data = self._rawObj.lastReadRaw
        if dataFormat.startswith('ASC'):
            data = self.__interpretAsciiFormat(data, dtype)
        else:

            data = self.__interpretBinaryFormat(data, dataFormat, dtype)
        if data is None:
            return numpy.fromstring("", dtype=dtype)
        return data

    def __interpretAsciiFormat(self, data, dtype):
        if data[0] == '#':
            bodyBlock = self.__interpretHeader(data)
            if not bodyBlock:
                self.error_stream('Impossible to interpret the header')
                return
            if dtype == numpy.bool:
                return numpy.array([bool(i.lower() not in ['0', 'false'])
                                    for i in bodyBlock.split(',')])
            else:
                return numpy.fromstring(bodyBlock, dtype=dtype, sep=',')
        else:
            try:
                if dtype == numpy.bool:
                    return numpy.array(
                        [bool(i.lower() not in ['0', 'false', 'off'])
                         for i in data.split(',')])
                else:
                    return numpy.fromstring(data, dtype=dtype, sep=',')
            except Exception as e:
                self.error_stream("Impossible to interpret raw data")
                self.debug_stream("Exception: %s" % (e))

    def __interpretBinaryFormat(self, data, dataFormat, dtype):
        format, divisor = self.__getFormatAndDivisor(dataFormat)
        bodyBlock = self.__interpretHeader(data)
        if not bodyBlock:
            self.error_stream('Impossible to interpret the header')
            return
        completBytes = self.__getCompleteBytes(bodyBlock, divisor)
        unpackedData = self.__unpackBytes(data, format, divisor)
        if unpackedData:
            floats = numpy.array(unpackInt, dtype=dtype)
            return self._Origin + (self._increment * floats)

    def __interpretHeader(self, buffer):
        if buffer[0] == '#' and len(buffer) > 2:
            headerSize = int(buffer[1])
            if len(buffer) > 2+headerSize:
                bodySize = int(buffer[2:2+headerSize])
                bodyBlock = buffer[2+headerSize:2+headerSize+bodySize]
                self.debug_stream("In _headerInterpreter() waveform data: "
                                  "header size %d bytes, wave size %d bytes "
                                  "(%d)" % (2+headerSize, bodySize,
                                            len(bodyBlock)))
                return bodyBlock

    def __getFormatAndDivisor(self, dataFormat):
        format, divisor = interpret_binary_format(dataFormat)
        self.debug_stream("dataFormat %s: unpack with %s, %d"
                          % (dataFormat, format, divisor))
        return format, divisor

    def __getCompleteBytes(self, buffer, divisor):
        nIncompleteBytes = (len(buffer) % divisor)
        nCompletBytes = len(buffer) - nIncompleteBytes
        completBytes = buffer[:nCompletBytes]
        self.debug_stream("With %d bytes, found %d complete packs "
                          "and %d incomplete. (Expected %d single "
                          "values)" % (len(buffer), nCompletBytes,
                                       nIncompleteBytes,
                                       nCompletBytes/divisor))
        return completBytes

    def __unpackBytes(self, data, format, divisor):
        lenData = len(data)
        try:
            fmt = format*(lenData/divisor)
            self.debug_stream("Preparing to unpack with %r format "
                              "(len fmt %d, len bytes %d)"
                              % (format, len(fmt), lenData))
            return struct.unpack(fmt, data)
        except Exception as e:
            self.error_stream("Data cannot be unpacked")
            self.debug_stream("Exception: %s" % (e))
            traceback.print_exc()
