from __future__ import print_function
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
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

try:
    import argparse
except:
    argparse = None
from datetime import datetime
from instrAttrs import (ROinteger, RWinteger, ROfloat, RWfloat,
                        ROIntegerFallible, Format,
                        ROIntegerArray, ROFloatArray, Waveform,
                        ROboolean, RWboolean, ROBooleanArray, ROFloatChannel)
from instrIdn import InstrumentIdentification, __version__
from psutil import process_iter, Process
import PyTango
import signal
import scpilib
from select import select
from subprocess import Popen, PIPE
import sys
from time import sleep
import traceback

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


DevServer = 'Skippy'
DevInstance = 'FakeInstrument'
DevClass = 'Skippy'
DevName = 'fake/skyppy/instrument-01'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FakeInstrument(object):

    _identity = None
    _scpiObj = None
    _attrObjs = {}

    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._buildFakeSCPI()

    def _buildFakeSCPI(self):
        version = "%s+scpilib_%s" % (__version__, scpilib.version.version())
        self._identity = InstrumentIdentification('FakeInstruments. Inc',
                                                  'Tester', 0, version)
        self._scpiObj = scpilib.scpi(local=True, debug=True, log2File=True,
                                     loggerName="SkippyTester")
        self._buildSpecialCommands()
        self._buildNormalCommands()
        self.open()

    def __str__(self):
        return "%s" % self._scpiObj

    def __repr__(self):
        return "%r" % self._scpiObj

    def tree(self):
        return "%r" % self._scpiObj._commandTree

    def open(self):
        self._scpiObj.open()

    def close(self):
        self._scpiObj.close()

    def _buildSpecialCommands(self):
        self._scpiObj.addSpecialCommand('IDN', self._identity.idn)

    def _buildNormalCommands(self):
        self._attrObjs['roboolean'] = self.__build_ROBoolean()
        self._attrObjs['rwboolean'] = self.__build_RWBoolean()
        self._attrObjs['rointeger'] = self.__build_ROInteger()
        self._attrObjs['rwinteger'] = self.__build_RWInteger()
        self._attrObjs['rofloat'] = self.__build_ROfloat()
        self._attrObjs['rwfloat'] = self.__build_RWfloat()
        self._attrObjs['rampeable'] = self.__build_RampeableFloat()
        self._attrObjs['fallible'] = self.__build_FallibleInteger()
        self._attrObjs['formatarray'] = self.__build_ArrayFormater()
        self._attrObjs['originarray'] = self.__build_ArrayOrigin()
        self._attrObjs['incrementarray'] = self.__build_ArrayIncrement()
        self._attrObjs['robooleanarray'] = self.__build_ROBooleanArray()
        self._attrObjs['rointegerarray'] = self.__build_ROIntegerArray()
        self._attrObjs['rofloatarray'] = self.__build_ROFloatArray()
        self._attrObjs['waveform'] = self.__build_Waveform()
        self._attrObjs['rofloatarray_ch'] = self.__build_ROFloatArray_Ch()
        self._attrObjs['rofloatarray_fn'] = self.__build_ROFloatArray_Fn()
        # self._attrObjs['multiple'] = self._build_ROFloatArray_Multiple()

    def __build_ROBoolean(self):
        robooleanObj = ROboolean()
        self._scpiObj.addCommand('source:readable:boolean:value',
                                 readcb=robooleanObj.value, default=True)
        return robooleanObj

    def __build_RWBoolean(self):
        rwbooleanObj = RWboolean()
        self._scpiObj.addCommand('source:writable:boolean:value',
                                 readcb=rwbooleanObj.value,
                                 writecb=rwbooleanObj.value,
                                 default=True)
        return rwbooleanObj

    def __build_ROInteger(self):
        rointegerObj = ROinteger()
        self._scpiObj.addCommand('source:readable:short:value',
                                 readcb=rointegerObj.value, default=True)
        self._scpiObj.addCommand('source:readable:short:upper',
                                 readcb=rointegerObj.upperLimit,
                                 writecb=rointegerObj.upperLimit)
        self._scpiObj.addCommand('source:readable:short:lower',
                                 readcb=rointegerObj.lowerLimit,
                                 writecb=rointegerObj.lowerLimit)

        return rointegerObj

    def __build_RWInteger(self):
        rwinteger = RWinteger()
        self._scpiObj.addCommand('source:writable:short:value',
                                 readcb=rwinteger.value,
                                 writecb=rwinteger.value,
                                 default=True)
        self._scpiObj.addCommand('source:writable:short:upper',
                                 readcb=rwinteger.upperLimit,
                                 writecb=rwinteger.upperLimit)
        self._scpiObj.addCommand('source:writable:short:lower',
                                 readcb=rwinteger.lowerLimit,
                                 writecb=rwinteger.lowerLimit)
        return rwinteger

    def __build_ROfloat(self):
        rofloat = ROfloat()
        self._scpiObj.addCommand('source:readable:float:value',
                                 readcb=rofloat.value, default=True)
        self._scpiObj.addCommand('source:readable:float:upper',
                                 readcb=rofloat.upperLimit,
                                 writecb=rofloat.upperLimit)
        self._scpiObj.addCommand('source:readable:float:lower',
                                 readcb=rofloat.lowerLimit,
                                 writecb=rofloat.lowerLimit)
        return rofloat

    def __build_RWfloat(self):
        rwfloat = RWfloat()
        self._scpiObj.addCommand('source:writable:float:value',
                                 readcb=rwfloat.value,
                                 writecb=rwfloat.value,
                                 default=True)
        self._scpiObj.addCommand('source:writable:float:upper',
                                 readcb=rwfloat.upperLimit,
                                 writecb=rwfloat.upperLimit)
        self._scpiObj.addCommand('source:writable:float:lower',
                                 readcb=rwfloat.lowerLimit,
                                 writecb=rwfloat.lowerLimit)
        return rwfloat

    def __build_RampeableFloat(self):
        rampeable = RWfloat()
        self._scpiObj.addCommand('rampeable:value',
                                 readcb=rampeable.value,
                                 writecb=rampeable.value,
                                 default=True)
        self._scpiObj.addCommand('rampeable:upper',
                                 readcb=rampeable.upperLimit,
                                 writecb=rampeable.upperLimit)
        self._scpiObj.addCommand('rampeable:lower',
                                 readcb=rampeable.lowerLimit,
                                 writecb=rampeable.lowerLimit)
        return rampeable

    def __build_FallibleInteger(self):
        fallible = ROIntegerFallible()
        self._scpiObj.addCommand('fallible:value',
                                 readcb=fallible.value,
                                 writecb=fallible.value,
                                 default=True)
        self._scpiObj.addCommand('fallible:upper',
                                 readcb=fallible.upperLimit,
                                 writecb=fallible.upperLimit)
        self._scpiObj.addCommand('fallible:lower',
                                 readcb=fallible.lowerLimit,
                                 writecb=fallible.lowerLimit)
        return fallible

    def __build_ArrayFormater(self):
        formatarray = Format()
        self._scpiObj.addCommand('dataformat',
                                 readcb=formatarray.value,
                                 writecb=formatarray.value)
        return formatarray

    def __build_ArrayOrigin(self):
        origin4arrays = RWfloat()
        self._scpiObj.addCommand('dataorigin',
                                 readcb=origin4arrays.value,
                                 writecb=origin4arrays.value)
        return origin4arrays

    def __build_ArrayIncrement(self):
        increment4arrays = RWfloat()
        self._scpiObj.addCommand('dataincrement',
                                 readcb=increment4arrays.value,
                                 writecb=increment4arrays.value)
        return increment4arrays

    def __build_ROBooleanArray(self):
        robooleanarray = ROBooleanArray()
        self._scpiObj.addCommand('source:readable:array:boolean:value',
                                 readcb=robooleanarray.value, default=True)
        return robooleanarray

    def __build_ROIntegerArray(self):
        rointegerarray = ROIntegerArray()
        self._scpiObj.addCommand('source:readable:array:short:value',
                                 readcb=rointegerarray.value, default=True)
        self._scpiObj.addCommand('source:readable:array:short:upper',
                                 readcb=rointegerarray.upperLimit,
                                 writecb=rointegerarray.upperLimit)
        self._scpiObj.addCommand('source:readable:array:short:lower',
                                 readcb=rointegerarray.lowerLimit,
                                 writecb=rointegerarray.lowerLimit)
        self._scpiObj.addCommand('source:readable:array:short:samples',
                                 readcb=rointegerarray.samples,
                                 writecb=rointegerarray.samples)
        return rointegerarray

    def __build_ROFloatArray(self):
        rofloatarray = ROFloatArray()
        self._scpiObj.addCommand('source:readable:array:float:value',
                                 readcb=rofloatarray.value, default=True)
        self._scpiObj.addCommand('source:readable:array:float:upper',
                                 readcb=rofloatarray.upperLimit,
                                 writecb=rofloatarray.upperLimit)
        self._scpiObj.addCommand('source:readable:array:float:lower',
                                 readcb=rofloatarray.lowerLimit,
                                 writecb=rofloatarray.lowerLimit)
        self._scpiObj.addCommand('source:readable:array:float:samples',
                                 readcb=rofloatarray.samples,
                                 writecb=rofloatarray.samples)
        return rofloatarray

    def __build_ROFloatArray_Ch(self):
        return self.__build_ROFloatArray_aux('channel', 4)

    def __build_ROFloatArray_Fn(self):
        return self.__build_ROFloatArray_aux('functions', 8)

    def __build_ROFloatArray_aux(self, name, how_many):
        root_obj = self._scpiObj._commandTree
        source_obj = self._scpiObj.addComponent('source', root_obj)
        readable_obj = self._scpiObj.addComponent('readable', source_obj)
        channels_obj = self._scpiObj.addChannel(name, how_many, readable_obj)
        rofloatarray_ch = ROFloatChannel(how_many)
        for i in range(1, how_many+1):

            floatcomponent_obj = self._scpiObj.addComponent(
                'float', channels_obj)
            for (attrName, cb_func) in \
                    [('upper', rofloatarray_ch.upperLimit),
                     ('lower', rofloatarray_ch.lowerLimit),
                     ('samples', rofloatarray_ch.samples),
                     ('switch', rofloatarray_ch.switch),
                     ('value', rofloatarray_ch.value)]:
                if attrName == 'value':
                    default = True
                else:
                    default = False
                self._scpiObj.addAttribute(
                    attrName, floatcomponent_obj,
                    readcb=cb_func, writecb=cb_func, default=default)
        return rofloatarray_ch

    def _build_ROFloatArray_Multiple(self):
        pass


    def __build_Waveform(self):
        # TODO: this should become a test for channel as well as state for them
        waveform = Waveform()
        self._scpiObj.addCommand('source:switchable:array:float:value',
                                 readcb=waveform.value, default=True)
        self._scpiObj.addCommand('source:switchable:array:float:switch',
                                 readcb=waveform.switch,
                                 writecb=waveform.switch)
        self._scpiObj.addCommand('source:switchable:array:float:samples',
                                 readcb=waveform.samples,
                                 writecb=waveform.samples)
        self._scpiObj.addCommand('source:switchable:array:float:periods',
                                 readcb=waveform.periods,
                                 writecb=waveform.periods)
        return waveform



global manager
manager = None
global exitCode
exitCode = -1


class TestManager(object):

    _deviceProcess = None

    def __init__(self, *args, **kwargs):
        super(TestManager, self).__init__(*args, **kwargs)
        self._instrument = FakeInstrument()
        self.log("FakeInstrument build: %r" % (self._instrument))
        self.log("\tCommand tree: %s" % (self._instrument.tree()))
        self._createTestDevice()
        self._startTestDevice()

    def __del__(self):
        self._stopTestDevice()
        self._deleteTestDevice()

    def log(self, msg, color=None):
        if color:
            print(color+"%s" % (msg)+bcolors.ENDC)
        else:
            print("%s" % (msg))

    def _createTestDevice(self):
        tangodb = PyTango.Database()
        self.log(
            "Creating a {0} device in {1}:{2}".format(
                DevName, tangodb.get_db_host(), tangodb.get_db_port()),
            color=bcolors.HEADER)
        devInfo = PyTango.DbDevInfo()
        devInfo.name = DevName
        devInfo._class = DevClass
        devInfo.server = DevServer+"/"+DevInstance
        tangodb.add_device(devInfo)
        self.log("Server {0} added".format(DevServer+"/"+DevInstance),
                 color=bcolors.OKBLUE)
        for (propertyName, propertyValue) in \
                [['Instrument', 'localhost'],
                 ['NumChannels', '4'], ['NumFunctions', '8']]:
            _property = PyTango.DbDatum(propertyName)
            _property.value_string.append(propertyValue)
            self.log(
                "Set property {0}: {1}".format(propertyName, propertyValue),
                color=bcolors.OKBLUE)
            tangodb.put_device_property(DevName, _property)

    def _startTestDevice(self):
        if not self._isAlreadyRunning():
            try:
                self._deviceProcess = Popen([DevServer, DevInstance, "-v4"])
            except OSError:
                launcher = "/usr/lib/tango/"+DevServer
                self._deviceProcess = Popen([launcher, DevInstance, "-v4"])
            self.log("Launched the device server has pid %d"
                     % (self._deviceProcess.pid), color=bcolors.OKBLUE)
        else:
            self.log("Test device already running!", color=bcolors.WARNING)

    def _stopTestDevice(self):
        if self._deviceProcess is None:
            return
        process = Process(self._deviceProcess.pid)
        if not self.__stopProcess(process):
            self.log(" Process %d needs to be killed" % (process.pid),
                     color=bcolors.WARNING)
            self.__killProcess(process)
        self.log("Test device stopped")

    def __stopProcess(self, process):
        nChildren = len(process.children())
        if nChildren > 0:
            self.log("Process %d has %d children to be stopped"
                     % (process.pid, nChildren), color=bcolors.OKBLUE)
            for child in process.children():
                if not self.__stopProcess(child):
                    self.log("Process %d still running, proceed to kill"
                             % (child.pid), color=bcolors.WARNING)
                    self.__killProcess(child)
        process.terminate()
        for i in range(10):  # 1 second waiting
            if not process.is_running():
                return True
            print(".", end='')  # , flush=True) # it is not that future
            sys.stdout.flush()
            process.terminate()
            sleep(0.1)
        return False

    def __killProcess(self, process):
        try:
            process.kill()
        except:
            pass

    def _deleteTestDevice(self):
        try:
            tangodb = PyTango.Database()
            self.log("Remove a %s device in %s:%s"
                     % (DevName, tangodb.get_db_host(), tangodb.get_db_port()),
                     color=bcolors.OKBLUE)
            tangodb.delete_device(DevName)
            tangodb.delete_server(DevServer+"/"+DevInstance)
        except Exception as e:
            self.log("* Deletion failed, please review manually "
                     "for garbage *\n", color=bcolors.FAIL)

    def _isAlreadyRunning(self):
        procs = []
        for proc in process_iter():
            if proc.name() == 'python':
                cmd = proc.cmdline()
                if len(cmd) == 3 and \
                        cmd[1].lower().startswith(DevServer.lower()) and\
                        cmd[2].lower() == DevInstance.lower():
                    self.log("found process %d" % (proc.pid))
                    procs.append(proc)
        if len(procs) == 0:
            return False
        if len(procs) > 1:
            self.log("ALERT: the device seems to be running more than once",
                     color=bcolors.FAIL)
        return True

    def _isDeviceReady(self):
        if self._deviceProcess is None:
            return False
        try:
            deviceProxy = PyTango.DeviceProxy(DevName)
            self.log("Device is in %s state" % deviceProxy.State())
            return True
        except:
            return False

    # Tests ---
    def launchTest(self):
        while not self._isDeviceReady():
            self.log("Waiting the device", color=bcolors.WARNING)
            sleep(1)
        self.log("Start the test", color=bcolors.HEADER)
        deviceProxy = PyTango.DeviceProxy(DevName)
        # FIXME: once the scpilib supports it, the tests must be made with
        #  and without this flag raised.
        deviceProxy['ReadAfterWrite'] = True
        self.log("Testing {0} a read after write".format(
            "with" if deviceProxy['ReadAfterWrite'].value else "with out"))
        testMethods = [self.test_communications,
                       self.test_readings,
                       self.test_writes,
                       self.test_glitch,
                       self.test_waveform_switch,
                       self.test_dyn_attr_injection]
        reports = []
        for i, test in enumerate(testMethods):
            result, report = test(deviceProxy)
            if not result:
                return i+1
            if isinstance(report[0], list):
                reports += report
            else:
                reports.append(report)
        self.log("All tests passed", color=bcolors.HEADER)
        for name, msg in reports:
            self.log("\t%s:\t%s" % (name, msg))
        return 0

    def _checkTest(self, names, values):
        nones = [value is None for value in values]
        if any(nones):
            msg = bcolors.FAIL+"TEST FAILED"+bcolors.ENDC+":\n"
            for i, name in enumerate(names):
                msg = ''.join("%s\t%s = %r\n" % (msg, name, values[i]))
            return (False, msg)
        else:
            return (True, bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC)

    def test_communications(self, device):
        testTitle = "Communications"
        attrNames = ['QueryWindow', 'TimeStampsThreshold', 'ReadAfterWrite',
                     'State', 'Status']
        attrs = device.read_attributes(attrNames)
        values = [attr.value for attr in attrs]
        result, msg = self._checkTest(attrNames, values)
        self.log("%s:\t%s" % (testTitle, msg))
        return result, [testTitle, msg]

    def test_readings(self, device):
        testTitle = "Readings"
        excludeName = ['Idn', 'QueryWindow', 'TimeStampsThreshold', 'Version',
                       'ReadAfterWrite', 'State', 'Status',
                       'RampeableStep', 'RampeableStepSpeed', 'Fallible']
        excludePattern = {'startswith': ['Waveform', 'wfState', 'wfChannels']}
        attrNames = []
        results = []
        for attrName in device.get_attribute_list():
            if attrName in excludeName:
                continue  # next step in the loop
            in_the_loop = False
            for startstr in excludePattern['startswith']:
                if attrName.startswith(startstr):
                    in_the_loop = True
            if not in_the_loop:
                attrNames.append(attrName)
            # TODO: special attributes like ramps descriptors or spectra
        self.log("attributes for the %s test" % (testTitle),
                 color=bcolors.OKBLUE)
        for attrName in attrNames:
            self.log("\t{0}".format(attrName))
        reports = []
        for i in range(1, len(attrNames)+1):
            device['QueryWindow'] = i
            attrs = device.read_attributes(attrNames)
            values = [attr.value for attr in attrs]
            nones = [value is None for value in values]
            result, msg = self._checkTest(attrNames, values)
            self.log("Readings[%d]\t%s" % (i, msg))
            reports.append(["%s[%d]" % (testTitle, i), msg])
            if not result:
                return False, reports
            sleep(1.1*device['TimeStampsThreshold'].value)
        return True, reports

    def test_writes(self, device):
        testTitle = "Writes"
        attrNames = []
        values = []
        for attrName in device.get_attribute_list():
            if attrName.endswith('_rw'):
                rvalue = device[attrName].value
                if device[attrName].type == PyTango.DevFloat:
                    wvalue = int(rvalue/1.1) + (rvalue % 1)
                elif device[attrName].type == PyTango.DevShort:
                    wvalue = rvalue+1
                elif device[attrName].type == PyTango.DevBoolean:
                    wvalue = not rvalue
                self.log(
                    "*** {0} has {1} and going to write {2}".format(
                        attrName, rvalue, wvalue))
                device[attrName] = wvalue
                # Time between those two reads must be below the
                # 'TimeStampsThreshold' to check that, even the time hasn't
                # passed, it has been change by the write.
                sleep(0.05)
                new_rvalue = device[attrName].value
                self.log(
                    "*** {0}: had {1}, sent {2}, now {3}".format(
                        attrName, rvalue, wvalue, new_rvalue))
                if new_rvalue == wvalue:
                    values.append(wvalue)
                else:
                    values.append(None)
        result, msg = self._checkTest(attrNames, values)
        self.log("%s:\t%s" % (testTitle, msg))
        return result, [testTitle, msg]

    def test_glitch(self, device):
        testTitle = "Glitch"
        if device['State'].value in [PyTango.DevState.ON,
                                     PyTango.DevState.RUNNING]:
            if device.Exec("self.skippy.watchdogObj") == 'None':
                msg = "Device doesn't have the watchdog feature!"
                self.log(msg, color=bcolors.WARNING)
                return False, [testTitle, msg]
            reactiontime = device.Exec("self.skippy.watchdogObj.checkPeriod")
            self.log("reactiontime: %s" % reactiontime)
            reactiontime = float(reactiontime)
            t_0 = datetime.now()
            self._instrument.close()
            self.log("Instrument closed", color=bcolors.OKBLUE)
            reacted = self._waitUntilReaction(device, reactiontime,
                                              [PyTango.DevState.FAULT,
                                               PyTango.DevState.DISABLE])
            if not reacted:
                msg = "No device reaction after %s" % (datetime.now()-t_0)
                self.log(msg)
                fullmsg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + msg + bcolors.ENDC
                return False, [testTitle, fullmsg]
            self.log("Device has reacted", color=bcolors.OKBLUE)
            t_1 = datetime.now()
            self._instrument.open()
            self.log("Instrument reopened", color=bcolors.OKBLUE)
            reacted = self._waitUntilReaction(device, reactiontime,
                                              [PyTango.DevState.ON,
                                               PyTango.DevState.RUNNING])
            if not reacted:
                msg = "No device recovery after %s" % (datetime.now()-t_1)
                self.log(msg)
                fullmsg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + msg + bcolors.ENDC
                return False, [testTitle, fullmsg]
            self.log("Device has recovered", color=bcolors.OKBLUE)
            msg = bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC
            self.log("%s:\t%s" % (testTitle, msg))
            return True, [testTitle, msg]
        else:
            msg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + \
                    "Wrong device state %s" % (device['State'].value) \
                    + bcolors.ENDC
            self.log("%s:\t%s" % (testTitle, msg))
            return False, [testTitle, msg]

    def test_waveform_switch(self, device):
        testTitle = "Waveform Switch"
        self.log("attributes for the {0} test".format(testTitle),
                 color=bcolors.OKBLUE)

        def check():
            if switch is False and quality != PyTango.AttrQuality.ATTR_INVALID:
                raise Exception("Attributes read when shouldn't")
            elif switch is True and quality != PyTango.AttrQuality.ATTR_VALID:
                raise Exception("Attributes not read when should")

        try:
            waveformAttr = 'Waveform'
            switchAttr = 'Waveform_switch'
            quality = device[waveformAttr].quality
            switch = device[switchAttr].value
            check()
            device[switchAttr] = not switch
            quality = device[waveformAttr].quality
            switch = device[switchAttr].value
            check()
            device[switchAttr] = not switch
            msg = bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC
            self.log("%s:\t%s"%(testTitle, msg))
            return True, [testTitle, msg]
        except Exception as exc:
            msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, exc)
            self.log("{0}:\t{1}".format(testTitle, msg))
            return False, [testTitle, msg]

    def test_dyn_attr_injection(self, device):
        testTitle = "DynamicAttributes injection"
        try:
            tangodb = PyTango.Database()
            propertyName = "DynamicAttributes"
            _property = PyTango.DbDatum(propertyName)
            propertyValue = \
                'Attribute("float_scalar_ro_bis",\n' \
                '          {\'type\': PyTango.CmdArgType.DevFloat,\n' \
                '           \'dim\': [0],\n' \
                '           \'readCmd\': "source:readable:float:value?"\n' \
                '           })\n' \
                '\n' \
                'Attribute("float_scalar_rw_bis",\n' \
                '          {\'type\': PyTango.CmdArgType.DevFloat,\n' \
                '           \'dim\': [0],\n' \
                '           \'readCmd\': "source:writable:float:value?",\n' \
                '           \'writeCmd\': \n' \
                '               lambda value: "source:writable:float:"\n' \
                '                             "value {0}".format(value)\n' \
                '           })'
            _property.value_string.append(propertyValue)
            self.log(
                "Set property {0}: {1}".format(propertyName, propertyValue),
                color=bcolors.OKBLUE)
            tangodb.put_device_property(DevName, _property)
            if not device.updateDynamicAttributes():
                raise AssertionError("Device did NOT update the attributes")
            try:
                device['QueryWindow'] = 2
                attrs = device.read_attributes(['float_scalar_ro',
                                                'float_scalar_ro_bis'])
                values = [attr.value for attr in attrs]
                nones = [value is None for value in values]
                if any(nones):
                    raise AssertionError("ReadOnly read failed")
            except AssertionError as e:
                raise e
            except Exception as e:
                self.log(e, color=bcolors.FAIL)
                raise AssertionError(
                    "ReadOnly attribute did NOT work as expected")
            try:
                wait_time = device['TimeStampsThreshold'].value
                attrs = device.read_attributes(['float_scalar_rw',
                                                'float_scalar_rw_bis'])
                values = [attr.value for attr in attrs]
                if values[0] != values[1]:
                    raise AssertionError("ReadWrite read failed")
                rvalue = values[0]
                wvalue = int(rvalue / 1.1)+(rvalue % 1)
                device['float_scalar_rw'] = wvalue
                sleep(wait_time)
                if device['float_scalar_rw_bis'].value != wvalue:
                    raise AssertionError("ReadWrite write failed (1)")
                device['float_scalar_rw_bis'] = rvalue
                sleep(wait_time)
                if device['float_scalar_rw'].value != rvalue:
                    raise AssertionError("ReadWrite write failed (2)")
            except AssertionError as e:
                raise e
            except Exception as e:
                self.log(e, color=bcolors.FAIL)
                raise AssertionError(
                    "ReadWrite attribute did NOT work as expected")
        except Exception as exc:
            msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, exc)
            self.log("{0}:\t{1}".format(testTitle, msg))
            return False, [testTitle, msg]
        else:
            msg = bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC
            self.log("%s:\t%s"%(testTitle, msg))
            return True, [testTitle, msg]


    def _waitUntilReaction(self, device, reactionPeriod, statesLst):
        tries = 0
        state = device['State'].value
        while state not in statesLst:
            self.log("No device reaction yet... (%s)" % state,
                     bcolors.WARNING)
            sleep(reactionPeriod)
            tries += 1
            if tries == 10:
                return False
            state = device['State'].value
        self.log("Found a device reaction, state %s" % state)
        return True


def signalHandler(signum, frame):
    if signum == signal.SIGINT:
        print("\nCaptured a Ctrl+c: terminating the execution...")
    else:
        print("Unmanaged signal received (%d)" % (signum))


def main():
    global exitCode
    if argparse is not None:
        parser = argparse.ArgumentParser(description='Test the Skippy device '
                                         'server using a fake instrument.')
        parser.add_argument('--no-remove', dest='no_remove',
                            action="store_true",
                            # default=False,
                            help="don't destroy the test until the user say")
        args = parser.parse_args()
    else:
        class Object(object):
            no_remove = False
        args = Object()
    try:
        global manager
        manager = TestManager()
        sleep(3)
        manager.log("\n\tThe test is going to be launched",
                    color=bcolors.UNDERLINE)
        signal.signal(signal.SIGINT, signalHandler)
        sleep(3)
        exitCode = manager.launchTest()
        if args.no_remove:
            print("\n\tPress Ctrl+c to finish the fake device")
            signal.pause()
    except Exception as e:
        print("\nCannot complete the test: %s\n" % e)
        traceback.print_exc()
    finally:
        del manager
    sys.exit(exitCode)


if __name__ == '__main__':
    main()
