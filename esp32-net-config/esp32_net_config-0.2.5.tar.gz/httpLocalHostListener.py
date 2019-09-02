import socket
import gc
import time
import network

class HttpLocalHostListener:

    def __init__(self, numberOfListeners):
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        gc.collect()
        time.sleep(2)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(False)

        self.listener_socket.bind(('', 80))  # TODO: retry logic?...OSError:112
        self.listener_socket.listen(numberOfListeners)
