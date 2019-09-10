from ctypes import *
from swdclient.server_pb2 import *
# so = ctypes.cdll.LoadLibrary
# lib = so("./libswd.so")
import os

lib_path = os.path.abspath(__file__).replace("swdclient.py","libswd.so")

lib = CDLL(lib_path)


# lib.test()

# class SwdClient:
def start(ip = "127.0.0.1",port = 21567):
    lib.start(str(ip).encode() ,port)

lib.getData.argtypes=[POINTER(c_int)]
lib.getData.restype=POINTER(c_char)

def get_data():
    size = c_int(0)
    ptr = pointer(size)
    result = lib.getData(ptr)
    measurements = Measurements()
    measurements.ParseFromString(result[:size.value])
    return measurements

lib.sendData.argtypes=[c_float,c_float,c_float,c_bool,c_bool,c_float]
def control(throttle = 0,steer = 0,brake = 0,handBrake = False,reverse = False, speed = 0):
    lib.sendData(throttle,steer,brake,handBrake,reverse,speed)
