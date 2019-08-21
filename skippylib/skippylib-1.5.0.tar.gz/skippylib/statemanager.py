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

from .abstracts import AbstractSkippyObj
from PyTango import DevState

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class StateManager(AbstractSkippyObj):

    _state = DevState.UNKNOWN
    _allowedStates = [DevState.UNKNOWN, DevState.INIT, DevState.OFF,
                      DevState.STANDBY, DevState.ON, DevState.RUNNING,
                      DevState.MOVING,  # FIXME: special with ramped attrs.
                      DevState.ALARM, DevState.FAULT, DevState.DISABLE]
    _device = None

    def __init__(self, *args, **kwargs):
        super(StateManager, self).__init__(*args, **kwargs)
        if hasattr(self._parent, '_parent') and \
                self._parent._parent is not None:
            self._device = self._parent._parent
        self._important = []
        self._temporal = None
        self._stateCallbacks = {}
        self._statusCallbacks = {}
        self._alarmDueToMonitoring = []
        self._backupState = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._buildState(value)

    @property
    def status(self):
        return self._buildStatus()

    def setStateAndStatus(self, newState, newStatus, important=False):
        self._buildState(newState, inhibitStatus=True)
        self.addStatusMessage(newStatus, important)

    def _buildState(self, value, inhibitStatus=False):
        if value not in self._allowedStates:
            raise AssertionError("State %s not present in the Skippy state "
                                 "machine" % (value))
        if self._state != value:
            self.debug_stream("State change from %s to %s"
                              % (self._state, value))
            self._propagateState2Tango(value)
            self._callStateCallbacks()
            self._state = value
            if not inhibitStatus:
                self.cleanImportantMessages()

    def _buildStatus(self):
        msg = "The device is in %s state.\n" % (self.state)
        for each in self._important:
            msg = "%s%s\n" % (msg, each)
        if self._temporal is not None:
            msg = "%s%s\n" % (msg, self._temporal)
        self._propagateStatus2Tango(msg)
        self._callStatusCallbacks()
        self.debug_stream("New status message: %r" % (msg))
        return msg

    def addStatusMessage(self, newLine, important=False):
        if important:
            self._important.append("%s" % newLine)
        else:
            self._temporal = "%s" % newLine
        self._buildStatus()

    def cleanImportantMessages(self):
        self._important = []
        self._temporal = None
        self._buildStatus()

    def _propagateState2Tango(self, newState):
        if self._device is not None:
            self._device.push_change_event('State', newState)
            self._device.set_state(newState)

    def _propagateStatus2Tango(self, newStatus):
        if self._device is not None:
            self._device.push_change_event('Status', newStatus)
            self._device.set_status(newStatus)

    def subscribe2state(self, cb):
        i = 0
        while i in self._stateCallbacks:
            i += 1
        self._stateCallbacks[i] = cb
        return i

    def unsubscribe2state(self, id):
        self._stateCallbacks.pop(i)

    def subscribe2status(self, cb):
        i = 0
        while i in self._statusCallbacks:
            i += 1
        self._statusCallbacks[i] = cb
        return i

    def unsubscribe2status(self, id):
        self._statusCallbacks.pop(i)

    def _callStateCallbacks(self):
        for k, v in self._stateCallbacks.iteritems():
            self.debug_stream("Calling %dth state callback" % (k))
            try:
                v()
            except Exception as e:
                self.warning("%dth state callback exception: %s" % (k, e))

    def _callStatusCallbacks(self):
        for k, v in self._statusCallbacks.iteritems():
            self.debug_stream("Calling %dth status callback" % (k))
            try:
                v()
            except Exception as e:
                self.warning("%dth status callback exception: %s" % (k, e))

    def InsertAlarmDueToMonitoring(self, attrList):
        for attrName in attrList:
            if attrName not in self._alarmDueToMonitoring:
                self._alarmDueToMonitoring.append(attrName)
        self._checkMonitoringAlarm()

    def RemoveAlarmDueToMonitoring(self, attrList):
        for attrName in attrList:
            if self._alarmDueToMonitoring.count(attrName):
                self._alarmDueToMonitoring.pop(
                    self._alarmDueToMonitoring.index(attrName))
        self._checkMonitoringAlarm()

    def _checkMonitoringAlarm(self):
        if len(self._alarmDueToMonitoring) > 0:
            if self._state is not DevState.ALARM:
                self._backupState = self._state
                self._buildState(DevState.ALARM)
            self.cleanImportantMessages()
            self.addStatusMessage("Attributes %r required too much time "
                                  "to be read"
                                  % (self._alarmDueToMonitoring),
                                  important=True)
        if len(self._alarmDueToMonitoring) == 0 and \
                self._state is DevState.ALARM:
            self.cleanImportantMessages()
            self._buildState(self._backupState)
