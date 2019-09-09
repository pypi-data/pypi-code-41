import time
import socket
import threading
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

from quarchpy.disk_test.dtsGlobals import dtsGlobals

class DTSCommms:

    def __init__(self):
        self.standardHeader = "QuarchCSSelection"
        self.versionNumber = "1.01"
        pass


    def notifyChoiceOption(self, count, option):
        sendString = "QuarchDTS::" + str(count) + "=" + str(option)
        # Send to GUI server
        self.sendMsgToGUI(sendString)


    def newNotifyChoiceOption(self, type, dict, dictValue, moduleType = None ):
        sendString = ""
        if "module" in type:
            sendString = self.createXMLSelectionModule(dict, dictValue)
        elif "drive" in type:
            sendString = self.createXMLSelectionDrive(dict, dictValue, moduleType)

        sendString = "QuarchDTS::" + sendString

        print(sendString)

        self.sendMsgToGUI(sendString)


    """
    Function for any item being sent to GUI 
    Default is to wait 3 seconds, but can be set for longer / infinite
    """


    def sendMsgToGUI(self, toSend, timeToWait=5):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       # print("IP : " + str(dtsGlobals.GUI_TCP_IP))
        s.connect((dtsGlobals.GUI_TCP_IP, 9921))

        # TODO: Remove the print command
        # print("Item Sent across : " + toSend)
        toSend = str.encode(toSend)

        s.sendall(toSend + b"\n")
        # function for response + timeout

        # basically infinite wait
        if timeToWait is None:
            timeToWait = 999999

        self.processTimeoutAndResult(s, timeToWait)
        s.close()


    """
    Starts a subprocess to attempt to receive a return packet from java
    if timeout of 3 seconds is exceeded, break
    """


    def processTimeoutAndResult(self, socket, timeToWait):
        processObject = threading.Thread(target=self.getReturnPacket(socket))
        processObject.start()
        # timeout of 3 seconds
        start = time.time()
        while time.time() - start <= timeToWait:
            if processObject.is_alive():
                # print("Sleeping, timeout Left = " + str(TIMEOUT - (time.time() - start)))
                time.sleep(.1)  # Just to avoid hogging the CPU
            else:
                # All the processes are done, break now.
                break
        else:
            # We only enter this if we didn't 'break' above.
            # print("Response Timeout Reached")
            processObject.terminate()
            processObject.join()


    """
    reads data from socket passed
    """


    def getReturnPacket(self, socket):
        BUFFER_SIZE = 4096
        data = ""
        while (True):
            data = socket.recv(BUFFER_SIZE)
            if "OK" in bytes.decode(data):
                break
            if "choiceResponse" in bytes.decode(data):
                dtsGlobals.choiceResponse = data
                break
            if "STOP" in bytes.decode(data):
                # User requested to stop a test
                dtsGlobals.continueTest = False
                break
        return


    def createXMLSelectionDrive(self, key, values, driveType):

        top = Element(self.standardHeader)
        retString = ""

        # Drive types come in different dictionary types - different key names
        if "pcie" in driveType:

            child = SubElement(top, 'Name')
            child.text = str(values['vendor'])

            child = SubElement(top, 'Standard')
            child.text = str(values['slot'])

            child = SubElement(top, 'ConnType')
            child.text = str("PCIe")

            child = SubElement(top, 'XmlVersion')
            child.text = str(self.versionNumber)

            child = SubElement(top, 'itemType')
            child.text = str("Drive")

            # If backward compat needed with v1.01 QCS
            # retString = values["vendor"] + ", " + values["device"] + "=" + bytes.decode(tostring(top))

        elif "sas" in driveType:

            child = SubElement(top, 'Name')
            child.text = str(values['model'])

            child = SubElement(top, 'Standard')
            child.text = str(key)

            child = SubElement(top, 'ConnType')
            child.text = str("SAS")

            child = SubElement(top, 'itemType')
            child.text = str("Drive")

            child = SubElement(top, 'XmlVersion')
            child.text = str(self.versionNumber)

            # If backward compat needed with v1.01 QCS
            # retString = str(key) + "=" + values["model"] + ", " + values["size"] + "=" + bytes.decode(tostring(top))
            # print(retString)

        retString = bytes.decode(tostring(top))
        return retString


    def createXMLSelectionModule(self, dict, dictValue):

        top = Element(self.standardHeader)

        indexOfColon = dict.find(":")
        conType = str(dict[:indexOfColon])
        IpAddress = str(dict[indexOfColon + 1:])

        child = SubElement(top, 'ConnType')
        child.text = str(conType)

        child = SubElement(top, 'QtlNum')
        child.text = str(dictValue)

        child = SubElement(top, 'XmlVersion')
        child.text = str(self.versionNumber)

        child = SubElement(top, 'itemType')
        child.text = str("Module")

        if "TCP" in conType:
            child = SubElement(top, 'IpAddress')
            child.text = str(dict[indexOfColon + 1:])

        #return str(dict) + "=" + str(dictValue) + "=" + bytes.decode(tostring(top))
        return bytes.decode(tostring(top))