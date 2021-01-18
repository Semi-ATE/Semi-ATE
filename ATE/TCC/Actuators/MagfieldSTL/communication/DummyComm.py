from ATE.TCC.Actuators.MagfieldSTL.communication.CommunicationChannel import CommunicationChannel


class DummyCommunicationChannel(CommunicationChannel):

    def send(self, data):
        pass

    def receive(self, timeout):
        return ""

    def is_connected(self):
        return True
