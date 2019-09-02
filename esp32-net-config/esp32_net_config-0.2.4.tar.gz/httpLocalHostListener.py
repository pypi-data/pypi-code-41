import socket
import gc
import time


class HttpLocalHostListener:

    def __init__(self, numberOfListeners):
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        gc.collect()
        time.sleep(2)

        self.listener_socket.bind(('', 80))  # TODO: retry logic?...OSError:112
        self.listener_socket.listen(numberOfListeners)
