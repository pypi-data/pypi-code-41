from abc import ABC, abstractmethod
from publish_notifier.response import Response


class NotifierBase(ABC):
    """
    base class to notifiy the published message
    """

    def __init__(self, host, topic, configurations={}):
        self.host = host
        self.topic = topic
        self.configurations = configurations
        self.response = Response()

    @abstractmethod
    def _compress(self):
        pass

    @abstractmethod
    def _publish(self, data):
        pass
