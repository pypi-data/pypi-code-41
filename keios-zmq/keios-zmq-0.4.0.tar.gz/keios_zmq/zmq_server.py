from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ZMQMessage:
    identifier: str
    msg: bytearray


class ZMQServer(ABC):
    """
    server interface
    """

    @abstractmethod
    def start_server(self):
        pass

    @abstractmethod
    def close(self):
        pass
