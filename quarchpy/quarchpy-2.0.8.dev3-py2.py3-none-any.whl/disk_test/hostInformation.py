'''
Implements a cross platform system for scanning and querying system resources.

########### VERSION HISTORY ###########

06/05/2019 - Andy Norrie    - First version

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

from quarchpy.disk_test import driveTestConfig
from quarchpy.disk_test.dtsGlobals import dtsGlobals
from quarchpy.disk_test.dtsComms import DTSCommms
#from quarchpy.disk_test.driveTestCore import myGlobals
#from quarchpy.disk_test.driveTestCore import notifyChoiceOption, sendMsgToGUI, checkChoiceResponse, setChoiceResponse

# to make input function back compatible with Python 2.x
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


# defining this here means we will never have to differentiate
if platform.system() == 'Windows':
    from quarchpy.disk_test.lspci import WindowsLSPCI as lspci
    from quarchpy.disk_test.sasFuncs import WindowsSAS as sasDET

else:
    from quarchpy.disk_test.lspci import LinuxLSPCI as lspci
    from quarchpy.disk_test.sasFuncs import LinuxSAS as sasDET



class HostInformation:
    # creating new (private) class instance
    __mylspci = lspci()
    __mySAS = sasDET()
    internalResults = {}

    def _init_(self):
        pass

    '''
    Lists physical drives on the system, returning them in the form "{drive-type:identifier=drive description}"
    '''
    def list_physical_drives(self, drive_type, search_params=None):
        filter_drives = True

        # Get any additional parameters for the search
        if search_params is not None:
            if "filter_drives" in search_params:
                filter_drives = search_params["filter_drives"]

        user_devices = {}

        # PCIE devices are returned with an identifier number as the PCIe slot ID
        if drive_type.lower() == "pcie":

            pcie_scan_data = self.__mylspci.getPcieDeviceList()
            # Loop through PCIe results, pick only those matching the class code of a storage controller ([01xx]
            for pcie_name, pcie_device in pcie_scan_data.items():
                if "[01" in pcie_device["class"]:
                    # Add the device address and description to the dictionary
                    user_devices["pcie:" + pcie_device["slot"]] = pcie_device
                    # user_devices["pcie:" + pcie_device["slot"]] = pcie_device["vendor"] + ", " + pcie_device["device"]

            return user_devices

        elif drive_type.lower() == "sas":

            sas_scan_data = self.__mySAS.getSasDeviceList()

            for sas_name, sas_device in sas_scan_data.items():

                # windows interpretation
                if "description" in sas_device:
                    # windows version of sas
                    if "Disk drive" in sas_device["description"]:
                        # Add the device address and description to the dictionary
                        # user_devices["SAS:" + sas_device["name"]] = sas_device["model"] + ", " + sas_device["size"]
                        user_devices["SAS:" + sas_device["name"]] = sas_device

                # linux interpretation
                if "transport" in sas_device:
                    # linux version of sas
                    if "sas" in sas_device["transport"].lower():
                        # Add the device address and description to the dictionary
                        # user_devices["SAS:" + sas_device["Conn_Type"]] = sas_device["vendor"] + " " + sas_device["model"] + ", " + sas_device["size"]
                        user_devices["SAS:" + sas_device["Conn_Type"]] = sas_device

            return user_devices

    '''
    Returns a dictionary of status elements for the given device.
    '''
    def get_device_status(self, device_id):
        # If a PCIe device
        if device_id.find("pcie") == 0:
            # Get the status of the PCIe device and return it
            return self.__mylspci.getPcieDeviceDetailedInfo(devicesToScan=device_id)
        else:
            # currently would be in form sas:nameofDrive
            return self.__mySAS.getSasDeviceDetailedInfo(devicesToScan=device_id)

    '''
    Verifies that the PCIe link stats are the same now as they were at the start of the test

    driveId=ID string of the drive to test
    '''
    def verifyDriveStats(self, uniqueID, driveId, mappingMode):
        if "pcie" in str(driveId).lower():
            # Get the expected stats
            expectedSpeed = self.internalResults[driveId + "_linkSpeed"]
            expectedWidth = self.internalResults[driveId + "_linkWidth"]

            # Get the current stats
            linkSpeed, linkWidth = self.__mylspci.getPcieLinkStatus(driveId, mappingMode)

            # if the speed and width is the same
            if (linkSpeed == expectedSpeed and linkWidth == expectedWidth):
                # Log a test success
                driveTestConfig.testCallbacks["TEST_LOG"](uniqueID, time.time(), "testResult",
                                                          "Drive link speed/width was maintained " + driveId,
                                                          os.path.basename(
                                                              __file__) + " - " + sys._getframe().f_code.co_name,
                                                          {"testResult": True})
                return True;
            # Else log a test failure
            else:
                changeDetails = "Was: " + expectedSpeed + "/" + expectedWidth + " Now: " + linkSpeed + "/" + linkWidth
                driveTestConfig.testCallbacks["TEST_LOG"](uniqueID, time.time(), "testResult",
                                                          "Drive link speed/width was NOT maintained for: " + driveId,
                                                          os.path.basename(
                                                              __file__) + " - " + sys._getframe().f_code.co_name,
                                                          {"testResult": False, "textDetails": changeDetails})
                return False
        else:
            driveTestConfig.testCallbacks["TEST_LOG"](uniqueID, time.time(), "testResult",
                                                      "Drive still ID'd - No record of speeds for : " + driveId,
                                                      os.path.basename(
                                                          __file__) + " - " + sys._getframe().f_code.co_name,
                                                      {"testResult": True, "textDetails": "No change"})
            return True

    '''
    Checks if the given device string is visible on the bus
    '''
    def isDevicePresent(self, deviceStr, mappingMode, driveType):
        cwd = os.getcwd()
        os.chdir( os.path.dirname(__file__))
        # Get current device list
        if "pcie" in str(driveType).lower():
            deviceList = self.__mylspci.getPcieDevices(mappingMode)
            if str(deviceStr).startswith("pcie"):
                deviceStr = deviceStr[5:]
        elif "sas" in str(driveType).lower():
            deviceList = self.__mySAS.getSasDeviceList()
            if not str(deviceStr).startswith("sas"):
                deviceStr = "SAS:" + deviceStr

            if "\\" in deviceStr and "." in deviceStr:
                deviceStr = deviceStr.replace("\\", "").replace(".","").replace("SAS:","")

        #print(deviceStr)
        #print(deviceList)

        os.chdir(cwd)

        # Loop through devices and see if our module is there
        for devStr in deviceList:
            if str(deviceStr).strip() in str(devStr).strip():
                return True
        return False


    def storeInitialDriveStats(self, driveId, linkSpeed, linkWidth):
        self.internalResults[driveId + "_linkSpeed"] = linkSpeed
        self.internalResults[driveId + "_linkWidth"] = linkWidth

    def getDriveList(self, mappingMode):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        # Get current device list
        deviceList = self.__mylspci.getPcieDevices(mappingMode)
        deviceList += self.__mySAS.getSasDeviceList()
        print(deviceList)
        os.chdir(cwd)
        return deviceList



    # '''
    # Prompts the user to view the list of PCIe devices and select the one to work with
    # '''
    # def pickPcieTarget(self, resourceName):
    #     # Check to see if the pcieMappingMode resource string is set
    #     mappingMode = driveTestConfig.testCallbacks["TEST_GETRESOURCE"]("pcieMappingMode")
    #     if (mappingMode == None):
    #         mappingMode = False
    #
    #     # Get the curent devices
    #     deviceStr = "NO_DEVICE_STRING"
    #     deviceList = self.__mylspci.getPcieDevices(mappingMode)
    #     deviceDict = {}
    #
    #     while self.devicePresentInList(deviceList, deviceStr) == False:
    #         # Print the list of devices
    #         # count = 0
    #         for pcieStr in deviceList:
    #             # split at first space
    #             moduleSections = pcieStr.split(" ", 1)  # splitting into ID and Desc
    #             deviceDict[moduleSections[0]] = moduleSections[1]  # Adding as key / value in dictionary
    #             print("Module ID : " + str(moduleSections[0]))
    #             print("Module Desc : " + str(moduleSections[1]))
    #
    #             # is send across in format QuarchDTS::Key=Value
    #             driveTestCore.notifyChoiceOption(moduleSections[0], moduleSections[1])
    #         if not deviceList:
    #             # python logic!
    #             print("ERROR - No PCIe devices found to display")
    #
    #         # Ask for selection -- Send as individual as to allow infinite wait for response
    #         driveTestCore.sendMsgToGUI("QuarchDTS::end-of-data", None)  # wait for response from java
    #         while driveTestCore.choiceResponse is None:
    #             time.sleep(0.25)
    #
    #         # choice response back should be.. choiceResponse::KEY
    #
    #         choice = bytes.decode(driveTestCore.choiceResponse)
    #         print("choice from user was : " + choice)
    #
    #         selection = choice.split("::")
    #         # order should be choiceResponse::xyz
    #         selection = selection[1]
    #
    #         # exit on 'q'
    #         if "choice-abort" in selection:
    #             return 0
    #
    #         # Validate selection
    #         found = False
    #         # need to change to string compare
    #
    #         for key, value in deviceDict.items():
    #             if selection.strip() == key:
    #
    #                 deviceStr = key
    #                 print("I found your device!")
    #                 found = True
    #                 break
    #
    #         if not found:
    #             print("couldn't find your device")
    #             return 0
    #
    #     # Get and store the initial link status of the selected device
    #     linkSpeed, linkWidth = self.__mylspci.getPcieLinkStatus(deviceStr, mappingMode)
    #     self.storeInitialDriveStats(deviceStr, linkSpeed, linkWidth)
    #     # Log the selection
    #     driveTestConfig.testCallbacks["TEST_LOG"](None, time.time(), "testDescription",
    #                                               "Device Selected: " + "PCIE:" + deviceStr + " - Speed:" + linkSpeed + ", Width:" + linkWidth,
    #                                               os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)
    #     # driveTestConfig.testCallbacks["TEST_LOG"](uId, logTime, messageType, messageText, messageSource, messageData)
    #     # print("here")
    #     # Store the device selection in the test resources
    #     driveTestConfig.testCallbacks["TEST_SETRESOURCE"](resourceName, "PCIE:" + deviceStr)

    '''
        Checks if the specified device exists in the list
        '''
    def devicePresentInList(self, deviceList, deviceStr):
        for pciStr in deviceList:
            if deviceStr in pciStr:
                return True
        return False

    '''
    Prompts the user to view the list of PCIe devices and select the one to work with
    '''
    def pickPcieTarget(self, resourceName, drive_type):

        comms = DTSCommms()

        dtsGlobals.choiceResponse = None

        # Check to see if the pcieMappingMode resource string is set
        mappingMode = driveTestConfig.testCallbacks["TEST_GETRESOURCE"]("pcieMappingMode")
        if (mappingMode == None):
            mappingMode = False

        # Get the current devices
        deviceStr = "NO_DEVICE_STRING"
        # deviceList = self.__mylspci.getPcieDevices(mappingMode)
        deviceDict = self.list_physical_drives(drive_type)
        # pcie_scan_data = self.__mylspci.getPcieDeviceList()
        # print(myGlobals.GUI_TCP_IP)

        # specify the module selection header
        comms.sendMsgToGUI("QuarchDTS::header::Choose a Drive to test", None)

        for key, value in deviceDict.items():
            # print("Key = " + key)
            # print("Value = " + value)
            # is send across in format QuarchDTS::Key=Value
            try:
                #comms.notifyChoiceOption(key, value)
                comms.newNotifyChoiceOption("drive", key, value, drive_type)
            except Exception as e:
                print(e)

        if not deviceDict:
            # python logic!
            print("ERROR - No PCIe devices found to display")

        # Ask for selection -- Send as individual as to allow infinite wait for response
        comms.sendMsgToGUI("QuarchDTS::end-of-data", None)  # wait for response from java

        while dtsGlobals.choiceResponse is None and dtsGlobals.continueTest is True:
            time.sleep(0.25)

        if (dtsGlobals.choiceResponse is None):
            return 0

        # choice response back should be.. choiceResponse::KEY

        choice = bytes.decode(dtsGlobals.choiceResponse)
        # print("choice from user was : " + choice)

        selection = choice.split("::")
        # order should be choiceResponse::xyz
        selection = selection[1]

        # exit on 'choice-abort' or if user stopped tests
        if "choice-abort" in selection or dtsGlobals.continueTest is False:
            return 0
        elif "rescan" in selection:
            return self.pickPcieTarget(resourceName, drive_type)

        # Validate selection
        found = False
        # need to change to string compare

        for key, value in deviceDict.items():
            if selection.strip() == key:
                deviceStr = key
                print("Device Found!")
                found = True
                break

        if not found:
            print("Device Not Found")
            return 0

        # Get and store the initial link status of the selected device
        if selection.lower().find("pcie") == 0:
            linkSpeed, linkWidth = self.__mylspci.getPcieLinkStatus(deviceStr, mappingMode)
            self.storeInitialDriveStats(deviceStr, linkSpeed, linkWidth)
            # Log the selection
            driveTestConfig.testCallbacks["TEST_LOG"](None, time.time(), "testDescription",
                                                  "Device Selected: " + "PCIE:" + deviceStr + " - Speed:" + linkSpeed + ", Width:" + linkWidth,
                                                  os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)
            # driveTestConfig.testCallbacks["TEST_LOG"](uId, logTime, messageType, messageText, messageSource, messageData)
            # Store the device selection in the test resources
            driveTestConfig.testCallbacks["TEST_SETRESOURCE"](resourceName, "PCIE:" + deviceStr)

        if selection.find("SAS") == 0:
            #linkSpeed, linkWidth = self.__mylspci.getPcieLinkStatus(deviceStr, mappingMode)
            #self.storeInitialDriveStats(deviceStr, linkSpeed, linkWidth)
            # Log the selection
            driveTestConfig.testCallbacks["TEST_LOG"](None, time.time(), "testDescription",
                                                  "Device Selected: " + deviceStr, # + " - Speed:" + linkSpeed + ", Width:" + linkWidth,
                                                  os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)
            # driveTestConfig.testCallbacks["TEST_LOG"](uId, logTime, messageType, messageText, messageSource, messageData)
            # Store the device selection in the test resources
            driveTestConfig.testCallbacks["TEST_SETRESOURCE"](resourceName, deviceStr)




    '''
    Checks if the script is runnin under admin permissions
    '''
    def checkAdmin(self):
        if self.__mylspci.is_admin_mode() == False:
            quit()


