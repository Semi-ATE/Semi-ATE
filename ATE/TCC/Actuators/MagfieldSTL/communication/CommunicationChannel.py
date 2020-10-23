from abc import ABC, abstractmethod


class CommunicationChannel(ABC):
    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def receive(self, timeout):
        pass

    @abstractmethod
    def is_connected(self):
        pass
