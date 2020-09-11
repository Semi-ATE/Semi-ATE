class Harness:
    '''
        The testharness is the interface used by
        the sequencer to interact with the remaining
        system components (i.e. the master!)

        On a fully running system it should house
        the MQTT connection logic
    '''

    def send_status(self, status):
        pass

    def send_testresult(self, stdfdata):
        pass

    def send_summary(self, summary):
        pass
