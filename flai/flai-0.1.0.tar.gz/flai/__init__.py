import socket
import select
from enum import Enum
from typing import Callable, Type, Tuple, List, Dict


class EpollSelector:
    def __init__(self):
        self.epoll = select.epoll()
        self._fd_with_sock: Dict[int, socket.socket] = dict()

    def register(self, sock: socket.socket, events: int):
        self._fd_with_sock[sock.fileno()] = sock
        self.epoll.register(sock.fileno(), events)

    def unregister(self, sock: socket.socket):
        self.epoll.unregister(sock.fileno())
        del self._fd_with_sock[sock.fileno()]

    def select(self) -> List[Tuple[socket.socket, int]]:
        return [
            (self._fd_with_sock[fd], event_mask) for fd, event_mask in self.epoll.poll()
        ]
    
    def close(self):
        self.epoll.close()
        for sock in self._fd_with_sock.values():
            sock.close()

class Flai:
    def __init__(self):
        self.selector = EpollSelector()
        self.routes: Dict[int, Callable[[bytes], None]] = dict()
        self.__request_type_size = 1
        self.__health_check_period = 5.

    def event(self, case: int) -> Callable[[bytes], None]:
        if case in self.routes:
            raise Exception("Duplicate option")

        def decorator(func):
            self.routes[case] = func
            return func

        return decorator

    @staticmethod
    def __create_server_socket(host: str, port: str) -> socket:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)

        server_address = (host, port)
        server.bind(server_address)

        server.listen(5)

        return server

    def run(self, host: str, port: int):
        self.server = self.__create_server_socket(host, port)
        self.selector.register(self.server, select.EPOLLIN)
        
        while True:
            selected = self.selector.select()
            for sock, events in selected:
                if sock is self.server:
                    client, address = self.server.accept()
                    print("Client connected from", address)
                    self.selector.register(client, select.EPOLLIN)
                else:
                    request_type = self._get_request_type(sock)
                    if request_type == 0:
                        print("Unregister,,, good bye :(")
                        self.selector.unregister(sock)
                    else:
                        if request_type in self.routes:
                            self.routes[request_type](sock.recv(1024))
                        else:
                            print("Not founded request type:", request_type)

    def _get_request_type(self, sock: socket.socket):
        request_type = int.from_bytes(sock.recv(self.__request_type_size), 'little')
        return request_type

    def close(self):
        self.selector.close()

flai = Flai()

@flai.event(1)
def handler(data: bytes):
    print('Received:', data)

flai.run("0.0.0.0", 9000)
