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
from copy import copy
from PyTango import DevState
from time import time, sleep
import traceback
from threading import Event, Thread

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class Monitor(AbstractSkippyObj):

    _attrLst = None

    def __init__(self, attrLst, *args, **kwargs):
        super(Monitor, self).__init__(*args, **kwargs)
        self._attrLst = attrLst
        self._multiattributeObj = self.__getMultiattributeObj()
        self._monitorThreads = {}
        self._generalMonitorEvent = Event()
        self._generalMonitorEvent.clear()
        self._monitoredAttributeIds = []
        self._alarmDueToMonitoring = []
        self.__prepareMonitor()

    @property
    def monitoredIds(self):
        return self._monitoredAttributeIds

    def __builtMonitorThread(self, name, period):
        scheleton = {'Name': name,  # Only used to output a message
                                    # when threads start
                     'Thread': None,
                     'Event': Event(),
                     'Period': period,
                     'AttrList': []}
        scheleton['Event'].clear()
        return scheleton

    def __getDevice(self):
        if self._parent and self._parent._parent:
            return self._parent._parent

    def __getMultiattributeObj(self):
        device = self.__getDevice()
        if device is not None and hasattr(device, 'get_device_attr'):
            return device.get_device_attr()

    def __getAttrId(self, attrName):
        if len(attrName) > 0:
            if self._multiattributeObj is not None:
                try:
                    return self._multiattributeObj.\
                        get_attr_ind_by_name(attrName)
                except Exception as e:
                    self.error_stream("get_attr_ind_by_name(%r) Exception: %s"
                                      % (attrName, e))
            id = 0
            while id in self._monitoredAttributeIds:
                id += 1
            return id

    def __buildIdList(self, attrList):
        device = self.__getDevice()
        if device is not None:
            multiattr = device.get_device_attr()
            IdsList = []
            for attrName in attrList:
                IdsList.append(multiattr.get_attr_ind_by_name(attrName))
            return IdsList

    def __prepareMonitor(self):
        ''' - The lines in the property 'MonitoredAttributes' defines an
            attribute name to be monitored (with an optional tag of an
            special period):
                attrName[:period]
            - The attributes must be stored in an Id way in a list, to
            simplify the filter when 'self.read_attr_hardware()' is called by
            a PyTango.DeviceProxy.read_attributes([]) or
            PyTango.DeviceProxy.read_attribute()
            - There is a thread for generic monitoring, the period of it
            is the 'TimeStampsThreashold' to have it as updated as possible.
            - Other periods will collect the ones with the same period in
              one thread.
            - The monitored attributes will have events.
        '''
#         self.debug_stream("list of attributes to monitor: %s"
#                           % (self._attrLst))
        if self._attrLst is None:
            return
        for attrName in self._attrLst:
            if not attrName.count(':'):  # Normal monitoring
                monitoringType = 'Generic'
                attrPeriod = self._parent.timestampsThreshold
                attrId = self.__getAttrId(attrName)
            else:
                attrName, attrPeriod = attrName.split(':')
                monitoringType = attrPeriod
                attrPeriod = float(attrPeriod)
                attrId = self.__getAttrId(attrName)
            # Once initialised they can be build by reference
            if attrName not in self._parent.attributes.keys():
                self.error_stream("The name %s is not an attribute in "
                                  "this device" % (attrName))
            elif attrId in self._monitoredAttributeIds:
                self.error_stream("The attribute %s is configured to "
                                  "be monitored more than one time"
                                  % (attrName))
            elif attrId is None:
                self.warn_stream("Attribute %r not found, ignoring")
            else:  # once here link it with the appropriate thread
                self.debug_stream("Preparing the attribute %s for "
                                  "the %s monitoring"
                                  % (attrName, monitoringType))
                self._monitoredAttributeIds.append(attrId)
                if monitoringType not in self._monitorThreads:
                    self._monitorThreads[monitoringType] = \
                        self.__builtMonitorThread(monitoringType,
                                                  attrPeriod)
                self._monitorThreads[monitoringType]['AttrList'].\
                    append(attrName)

    def Start(self):
        try:
            self._generalMonitorEvent.clear()
            for monitorTag in self._monitorThreads.keys():
                descriptor = self._monitorThreads[monitorTag]
                descriptor['Thread'] = Thread(target=self.__monitor,
                                              name="monitor",
                                              args=([descriptor]))
                descriptor['Event'].clear()
                descriptor['Thread'].setDaemon(True)
                if self.__getDevice() is not None:
                    for attrName in descriptor['AttrList']:
                        self.__set_change_event(attrName, True, False)
                descriptor['Thread'].start()
            self._change_state_status(newState=DevState.RUNNING)
        except Exception as e:
            self.error_stream("In %s.Start() Exception: %s" % (self.name, e))
            traceback.print_exc()

    def Stop(self):
        self.info_stream("In %s.Stop() waiting for %d"
                         % (self.name, len(self._monitorThreads.keys())))
        stopper = Thread(target=self.__doStop, name="monitor_stopper")
        stopper.setDaemon(True)
        stopper.start()

    def __monitor(self, monitorDict):
        '''This is the method where every monitor thread will live.
        '''
        self.info_stream("Monitoring thread '%s' announcing its START. "
                         "Attributes: %r" % (monitorDict['Name'],
                                             monitorDict['AttrList']))
        attrList = []
        while not self._generalMonitorEvent.is_set() and \
                not monitorDict['Event'].is_set():
            if not len(attrList) == len(monitorDict['AttrList']):
                attrList = copy(monitorDict['AttrList'])
                attrIds = self.__buildIdList(monitorDict['AttrList'])
                self.info_stream("In __monitor(), thread %s, the "
                                 "attribute list has change to %r"
                                 % (monitorDict['Name'],
                                    monitorDict['AttrList']))
            if len(attrList) == 0:
                monitorDict['Event'].set()
            else:
                t0 = time()
                self._parent._readAttrProcedure(attrIds, fromMonitor=True)
                tf = time()
                delta_t = monitorDict['Period'] - (tf - t0)
                if delta_t <= 0:  # it take longer than the period
                    self.__appendToAlarmCausingList(attrList)
                else:
                    self.__removeFromAlarmCausingList(attrList)
                    sleep(delta_t)
        self.info_stream("Monitoring thread %s announcing its STOP"
                         % (monitorDict['Name']))
        for AttrName in monitorDict['AttrList']:
            self.__set_change_event(AttrName, False, False)
        if monitorDict['Name'] in self._monitorThreads:
            self._monitorThreads.pop(monitorDict['Name'])

    def __doStop(self):
        self._generalMonitorEvent.set()
        while any([self._monitorThreads[monitorTag]['Thread'].isAlive()
                   for monitorTag in self._monitorThreads.keys()]):
            self.info_stream("In %s.Stop() waiting for %d"
                             % (self.name, len(self._monitorThreads.keys())))
            sleep(0.5)
        self._change_state_status(newState=DevState.ON)
        self.__prepareMonitor()

    def Insert(self, attrName, monitoringType):
        attrId = self.__getAttrId(attrName)
        if self._monitoredAttributeIds.count(attrId):
            self.warn_stream("Attribute %s already in the monitoring process"
                             % (attrName))
            return
        if monitoringType not in self._monitorThreads.keys():
            self.info_stream("%s monitoring thread doesn't exist, "
                             "creating" % (monitoringType))
            self._monitorThreads[monitoringType] = \
                self.__builtMonitorThread(attrName, attrPeriod)
        else:
            self.debug_stream("Adding %s to %s monitoring thread"
                              % (attrName, monitoringType))
        self._monitoredAttributeIds.append(attrId)
        self._monitorThreads[monitoringType]['AttrList'].append(attrName)
        self.__set_change_event(attrName, True, False)
        return attrId

    def Remove(self, attrId):
        if not self._monitoredAttributeIds.count(attrId):
            self.warn_stream("Attribute %s not present in the monitoring "
                             "process" % (attrName))
            return False
        for monitorKey in self._monitorThreads.keys():
            descriptor = self._monitorThreads[monitorKey]
            if descriptor['AttrList'].count(attrId):
                position = descriptor['AttrList'].index(attrId)
                descriptor['AttrList'].pop(position)
                self.__set_change_event(argin, False, False)
                break
        position = self._monitoredAttributeIds.index(attrId)
        self._monitoredAttributeIds.pop(position)
        return True

    def getPeriod(self, attrId):
        for monitorKey in self._monitorThreads.keys():
            descriptor = self._monitorThreads[monitorKey]
            if descriptor['AttrList'].count(argin):
                if monitorKey == 'Generic':
                    return self._parent.timestampsThreshold
                else:
                    return float(monitorKey)

    def changeGenericPeriod(self, value):
        if 'Generic' not in self._monitorThreads:
            self.error_stream("No generic period thread")
            return
        descriptor = self._monitorThreads['Generic']
        descriptor['Period'] = value

    def __set_change_event(self, attrName, implemented, detect):
        device = self.__getDevice()
        if device is not None:
            device.set_change_event(attrName, implemented, detect)

    def __appendToAlarmCausingList(self, attrList):
        if self._parent:
            statemachine = self._parent.statemachineObj
            statemachine.InsertAlarmDueToMonitoring(attrList)

    def __removeFromAlarmCausingList(self, attrList):
        if self._parent:
            statemachine = self._parent.statemachineObj
            statemachine.RemoveAlarmDueToMonitoring(attrList)
