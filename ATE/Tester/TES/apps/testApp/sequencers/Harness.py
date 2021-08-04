from abc import ABC, abstractclassmethod


class Harness(ABC):
    '''
        The testharness is the interface used by
        the sequencer to interact with the remaining
        system components (i.e. the master!)

        On a fully running system it should house
        the MQTT connection logic
    '''

    def __init__(self):
        pass

    @abstractclassmethod
    def next(self):
        pass

    @abstractclassmethod
    def collect(self, stdf_data: dict):
        pass

    @abstractclassmethod
    def send_testresult(self, stdf_data: dict):
        pass

    @abstractclassmethod
    def send_summary(self, summary: dict):
        pass
