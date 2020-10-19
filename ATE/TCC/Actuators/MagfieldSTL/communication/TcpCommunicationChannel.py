
from ATE.TCC.Actuators.MagfieldSTL.communication.CommunicationChannel import CommunicationChannel
import socket


from io import BytesIO
import select
import time


class TcpCommunicationChannel(CommunicationChannel):

    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = int(target_port)
        self.do_connect(target_ip, target_port)

    def do_connect(self, target_ip, target_port):
        num_retries = 0
        MAX_NUM_RETRIES = 5
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(1)
                self.sock.connect((target_ip, target_port))
                # Connection succeeded, return.
                print("Connected to DSC6k")
                return
            except Exception as ex:
                print(f"Failed to connect to DCS6k@{self.target_ip}:{self.target_port}. Retrying.")
                print(ex)
                time.sleep(2)
                num_retries = num_retries + 1
                if num_retries > MAX_NUM_RETRIES:
                    raise ex
                # ToDo: Check if we should use asyncio here, to avoid
                # blocking the mainloop if we lose the connection during
                # operation!

    def send(self, data):
        totalsent = 0
        msglen = len(data)
        while totalsent < msglen:
            sent = self.sock.send(data[totalsent:])
            if sent == 0:
                print("Lost connection to DCS6k, reconnect in progress..")
                self.do_connect(self.target_ip, self.target_port)
            totalsent = totalsent + sent

    def receive(self, timeout_ms):
        self.sock.settimeout(timeout_ms)
        buffer = BytesIO()
        while True:
            # read exactly one line from the socket:
            received = select.select([self.sock], [], [], timeout_ms / 1000.0)
            if not received[0]:     # timeout!
                return ""

            data = self.sock.recv(255)

            if len(data) == 0:
                # We return NO data in case of a connectionloss,
                # which is basically the same as a timeout.
                # We'll try to reconnect on the next send. Doing this
                # here makes no sense, as we probably have missed parts
                # of the packet we were trying to receive anyway.
                print("Lost connection to DCS6k")
                return ""

            buffer.write(data)
            buffer.seek(0)
            for line in buffer:
                return line

            # If we got here, we did not receive a complete line yet, so we
            # move the file pointer to the end and keep on receiving.
            buffer.seek(0, 2)
