from math import log10, floor
from socket import socket
from typing import List, Callable, Tuple


def eprint(*args, **kwargs):
    from sys import stderr
    print(*args, file=stderr, **kwargs)  # TODO Is there some warn(...) equivalent function?


def static_vars(**kwargs):
    """
    Decorator hack for introducing local static variables.
    :param kwargs: The declarations of the static variables like "foo=42".
    :return: The decorated function.
    """

    def decorate(func):
        """
        Decorates the given function with local static variables based on kwargs.
        :param func: The function to decorate.
        :return: The decorated function.
        """
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def create_server(port: int) -> socket:
    from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(1)  # FIXME Determine appropriate value
    return server_socket


def accept_at_server(server_socket: socket, on_accept: Callable[[socket, Tuple[str, int]], None]) -> None:
    while True:
        conn, addr = server_socket.accept()
        print(str(server_socket.getsockname()) + " accepted " + str(addr))
        on_accept(conn, addr)


def create_client(server_host: str, server_port: int) -> socket:
    from socket import AF_INET, SOCK_STREAM
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    return client_socket


CONTENT_LENGTH_LIMIT: int = 10000000  # 10 millions
# The length of the message transferring the content length
CONTENT_LENGTH_MESSAGE_LENGTH: int = floor(log10(CONTENT_LENGTH_LIMIT)) + 1
MAX_RETRY: int = 100


def _send_message(sock: socket, message: bytes) -> None:
    message_length = len(message)
    print(str(sock.getpeername()) + " sending " + str(message_length) + " bytes")
    if message_length > CONTENT_LENGTH_LIMIT:
        eprint("Can not send messages longer than " + str(CONTENT_LENGTH_LIMIT) + ".")
    else:
        message_length_message = str(message_length) \
            .ljust(CONTENT_LENGTH_MESSAGE_LENGTH, " ") \
            .encode()
        sock.sendall(message_length_message)
        sock.sendall(message)


# FIXME Introduce method receiving bytes until reaching a certain number
def _recv_message(sock: socket) -> bytes:
    print(str(sock.getsockname()) + " waiting for recv message length")
    tries = 0
    while tries < MAX_RETRY:
        content_length_message = sock.recv(CONTENT_LENGTH_MESSAGE_LENGTH).decode().strip()
        print(str(sock.getsockname()) + " got message length message: " + content_length_message)
        if content_length_message:
            content_length = int(content_length_message)
            print(str(sock.getsockname()) + " waits for receiving a message of length " + str(content_length))
            break
        else:
            tries = tries + 1
    else:
        eprint("Did not receive content length message.")
        return b""
    received_message = b""
    while len(received_message) < content_length:
        received_message = received_message + sock.recv(content_length - len(received_message))
    return received_message


def process_request(sock: socket, handle_message: Callable[[bytes, List[bytes]], bytes]) -> None:
    from drivebuildclient.aiExchangeMessages_pb2 import Num
    action = _recv_message(sock)
    print(str(sock.getsockname()) + " received action " + action.decode())
    num_data = Num()
    num_data.ParseFromString(_recv_message(sock))
    print(str(sock.getsockname()) + " received num_data " + str(num_data.num))
    data = []
    for _ in range(num_data.num):
        data.append(_recv_message(sock))
        print(str(sock.getsockname()) + " received data " + str(data[-1]))
    result = handle_message(action, data)
    print(str(sock.getsockname()) + " sends result")
    _send_message(sock, result)


def process_requests(waiting_socket: socket, handle_message: Callable[[bytes, List[bytes]], bytes]) -> None:
    # FIXME How to recover failures?
    try:
        while True:
            process_request(waiting_socket, handle_message)
    except (ConnectionAbortedError, ConnectionResetError):
        eprint("The socket " + str(waiting_socket.getsockname()) + " was closed.")


def send_request(sock: socket, action: bytes, data: List[bytes]) -> bytes:
    from drivebuildclient.aiExchangeMessages_pb2 import Num
    _send_message(sock, action)
    num_data = Num()
    num_data.num = len(data)
    if num_data.num == 0:
        num_data.num = -1
    _send_message(sock, num_data.SerializeToString())
    for d in data:
        _send_message(sock, d)
    return _recv_message(sock)
