from enum import Enum
class Protocol(Enum):
    CLEVERLAB = 1
    SILA2_0 = 2

import importlib

class DeviceDescriptor:
    def __init__(self, protocol, vendorURL, deviceType):
        if protocol == Protocol.CLEVERLAB:
            protocolName = "CL"
        elif protocol == Protocol.SILA2_0:
            protocolName = "SILA2"
        else:
            raise ValueError("invalid protocol '" + str(protocol) + "'")

        normalizedVendorURL = vendorURL # not changing currently
        normalizedDeviceTypeName = deviceType.replace("-", "_")

        self._vendorURL = vendorURL
        self._deviceType = deviceType

        self._instance = importlib.import_module("devices" + "." + protocolName + "." + normalizedVendorURL + "." + normalizedDeviceTypeName + "_pb2")

    def messageTypesAvailable(self):
        return self._instance.DESCRIPTOR.message_types_by_name.keys()

    def newMessage(self, messageName):
        if messageName not in self._instance.DESCRIPTOR.message_types_by_name:
            raise ValueError("no such message type " + messageName)

        return getattr(self._instance, messageName)()

    def getVendorURL(self):
        return self._vendorURL

    def getDeviceType(self):
        return self._deviceType

