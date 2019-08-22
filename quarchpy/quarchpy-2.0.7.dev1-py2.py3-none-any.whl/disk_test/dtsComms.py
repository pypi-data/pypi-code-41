import time
import socket
from datetime import datetime
import threading

from quarchpy.disk_test.dtsGlobals import dtsGlobals

class DTSCommms:

    def __init__(self):
        pass


    def notifyChoiceOption(self, count, option):
        sendString = "QuarchDTS::" + str(count) + "=" + str(option)
        # Send to GUI server
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
                print(data)
                break
        return