'''
Implements basic control over lspci utilities, so that we can identify and check the
status of PCIe devices on the host

########### VERSION HISTORY ###########

25/04/2018 - Andy Norrie    - First version
13/06/2019 - Andy Norrie    - Updated to contain base layer lspci API only
                              Other functions are now at a higher level

####################################
'''

import subprocess
import platform
import time
import os
import re
import sys
import ctypes
from abc import ABC, abstractmethod


# Class for others to 'extend'
class abstractSASDet(ABC):

    @abstractmethod
    def getSasDeviceList(self):
        pass

    @abstractmethod
    def getSasDeviceDetailedInfo(self, deviceInfo, devicesToScan):
        pass

    @abstractmethod
    def sortList(self, err, out):
        pass

    @abstractmethod
    def is_admin_mode(self):
        pass


class baseSASDet(abstractSASDet):
    def getSasDeviceList(self):
        pass

    def getSasDeviceDetailedInfo(self, deviceInfo, devicesToScan):
        pass

    def is_admin_mode(self):
        pass

    """
    Class independant method
    Takes same input
    produces same output
    """

    def sortList(self, err, out):
        pass

    def sortDeviceInfo(self, err, out, deviceInfo, devicesToScan):
        # Handle error output
        if (err):
            raise ValueError("lspci error: " + err.decode('utf-8'))
        out = out.decode('utf-8')

        # Split the output into blocks of each device (paragraph)
        blocks = out.split('\r\n\r\n')
        for desc in blocks:
            lnkStatSpeed = None
            lnkStatWidth = None
            lnkCapsSpeed = None
            lnkCapsWidth = None

            # Get the slot path of the current device
            pos = desc.find(' ')
            currDevice = desc[:pos]

            # Parse each potential section, handle missing sections and continue
            try:
                # Parse out link status
                strPos = desc.find('LnkSta:')
                statusText = desc[strPos:]
                matchObj = re.search('Speed (.*?),', statusText)
                lnkStatSpeed = matchObj.group(0)
            except:
                pass
            try:
                matchObj = re.search('Width (.*?),', statusText)
                lnkStatWidth = matchObj.group(0)
            except:
                pass
            try:
                # Parse out link capacity
                strPos = desc.find('LnkCap:')
                statusText = desc[strPos:]
                matchObj = re.search('Speed (.*?),', statusText)
                lnkCapsSpeed = matchObj.group(0)
            except:
                pass
            try:
                matchObj = re.search('Width (.*?),', statusText)
                lnkCapsWidth = matchObj.group(0)
            except:
                pass

            # Limit the devices to return, as requested
            if (devicesToScan == "all" or currDevice in devicesToScan):
                # If the device information does not already exists, create the extra stub
                if (currDevice not in deviceInfo):
                    deviceInfo[currDevice] = {}

                # Fill in the additional details
                deviceInfo[currDevice]["link_status:speed"] = lnkStatSpeed
                deviceInfo[currDevice]["link_status:width"] = lnkStatWidth
                deviceInfo[currDevice]["link_capability:speed"] = lnkCapsSpeed
                deviceInfo[currDevice]["link_capability:width"] = lnkCapsWidth
                deviceInfo[currDevice]["present"] = "true"

        # Check for any requested devices, which we did not find.  These must be marked as not present (rather than skipped)
        if (devicesToScan != "all"):
            blocks = devicesToScan.split('|')
            for currDevice in blocks:
                if currDevice not in deviceInfo:
                    deviceInfo[currDevice]["present"] = "false"

        # return the updated info structure
        return deviceInfo


class WindowsSAS(baseSASDet):
    def __init__(self):
        pass

    def is_admin_mode(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    '''
    Get basic information on all PCIe devices on the system.  Returned as a dictionary of dictionaries
    {nn:nn.n: {ELEMENT:DATA}}
    This is a fast way to scan the bus and see what is there before possible interrogating devices in more detail (device status and similar)
    '''

    def getSasDeviceList(self):

        # lspciPath = os.path.join(os.getcwd(), "pciutils", "lspci.exe")

        # call lspci to get a list of all devices and basic details in parable form
        proc = subprocess.Popen(["wmic", "diskdrive", "list", "full"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # "get", "Model,Size,Description,DeviceID"
        # Execute the process
        out, err = proc.communicate()
        retValues = self.sortList(err, out)

        # proc = subprocess.Popen(["wmic", "diskdrive", "list", "full"  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # "get", "Model,Size,Description,DeviceID"
        # Execute the process
        # out, err = proc.communicate()

        # print(bytes(out).decode())
        # retValues = sortList(err,out)

        return retValues

    '''
    Gets more detailed device information on one or more PCIe bus devices.  Each device info requires a seperate lcpci call
    Optionally pass in the info dictionary from getPcieDeviceInfo() in order to fill in the additional details
    devicesToScan is a CSV list of PCIe slot addresses.
    '''

    def getSasDeviceDetailedInfo(self, deviceInfo=None, devicesToScan="all"):

        # Setup the info structure, filling it if an 'all' selection is given but it is currently empty
        if (deviceInfo == None and devicesToScan == "all"):
            deviceInfo = getPcieDeviceInfo()
        elif (deviceInfo == None):
            deviceInfo = {}
            devicesToScan = devicesToScan[5:]

        # Run the lspci command
        lspciPath = os.path.join(os.getcwd(), "pciutils", "lspci.exe")

        # call lspci to get detailed information on devices
        proc = subprocess.Popen([lspciPath, '-vvvs', devicesToScan], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Execute the process
        out, err = proc.communicate()

        retValue = super().sortDeviceInfo(err, out, deviceInfo, devicesToScan)

        return retValue

    def sortList(self, err, out):
        SasDevices = {}

        unsorted = bytes(out).decode()

        deviceList = unsorted.split("\r\n\r\r")
        # print(len(deviceList))

        for dev in deviceList:
            if str(dev).strip() == "":
                continue
                # print("New Device: \r" +  dev)
            newDevice = {}
            for line in iter(dev.splitlines()):
                pos = line.find('=')
                if (pos != -1):
                    # Add the dictionary item
                    newDevice[line[:pos].lower()] = line[pos + 1:].strip()

            if ("name" in newDevice):
                SasDevices[newDevice["name"]] = newDevice

        return SasDevices


class LinuxSAS(baseSASDet):
    def __init__(self):
        pass

    def is_admin_mode(self):
        if os.getuid() == 0:
            return True
        else:
            return False

    '''
    Get basic information on all PCIe devices on the system.  Returned as a dictionary of dictionaries
    {nn:nn.n: {ELEMENT:DATA}}
    This is a fast way to scan the bus and see what is there before possible interrogating devices in more detail (device status and similar)
    '''

    def getSasDeviceList(self):

        # call lspci to get a list of all devices and basic details in parable form
        proc = subprocess.Popen(["lspci", "-mmvvvnn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # REQUIRES TESTING ON LINUX

        # Execute the process
        out, err = proc.communicate()

        print(bytes(out).decode())

        # will supply a dictionary - calls base class
        return super().sortList(err, bytes(out))

    '''
    Gets more detailed device information on one or more PCIe bus devices.  Each device info requires a seperate lcpci call
    Optionally pass in the info dictionary from getPcieDeviceInfo() in order to fill in the additional details
    devicesToScan is a CSV list of PCIe slot addresses.
    '''

    def getSasDeviceDetailedInfo(self, deviceInfo=None, devicesToScan="all"):

        # Setup the info structure, filling it if an 'all' selection is given but it is currently empty
        if (deviceInfo == None and devicesToScan == "all"):
            deviceInfo = getPcieDeviceInfo()
        elif (deviceInfo == None):
            deviceInfo = {}
            devicesToScan = devicesToScan[5:]

        # call lspci to get detailed information on devices
        proc = subprocess.Popen(["lspci", '-vvvs', devicesToScan], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # proc = subprocess.Popen(["lspci", '-vvvs', devicesToScan], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Execute the process
        out, err = proc.communicate()

        retValue = super().sortDeviceInfo(err, out, deviceInfo, devicesToScan)

        return retValue

    def getPcieDeviceInfo(self):
        # stubbing for the time being
        return None




