import socket

from ..config import conf


class MailClient:
    def __init__(self, name: str):
        self.config = conf.mail[name]
        addr = conf.home / 'mail' / name / 'socket'
        self.sock = socket.socket(socket.AF_UNIX)
        try:
            self.sock.connect(str(addr))
        except FileNotFoundError:
            from .server import Server
            Server(name).fork()
            self.sock.connect(str(addr))

    def get_folder(self, folder):
        """
        s.send(' '.join(sys.argv[2:]).encode())
        if sys.argv[2] != 'stop':
            print(pickle.loads(b''.join(iter(lambda: s.recv(8096), b''))))
        """
