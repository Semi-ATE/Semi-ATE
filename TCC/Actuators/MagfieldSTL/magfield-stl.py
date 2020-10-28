import argparse
from ATE.TCC.Actuators.common.mqtt.mqttbridge import MqttBridge
from ATE.TCC.Actuators.MagfieldSTL.communication.TcpCommunicationChannel import TcpCommunicationChannel
from ATE.TCC.Actuators.MagfieldSTL.driver.stldcs6k import DCS6K
from ATE.TCC.Actuators.MagfieldSTL.magfieldimpl.magfieldimpl import MagFieldImpl
from ATE.common.logger import (Logger, LogLevel)

import asyncio

parser = argparse.ArgumentParser(description="Magfield-STL implementation")
parser.add_argument("broker_ip", type=str, metavar="ip", help="Address of the mqtt broker to connect to")
parser.add_argument("broker_port", type=int, metavar="port", help="Port of the mqtt broker to connect to")
parser.add_argument("device_id", type=str, metavar="devid", help="Id of the testing device this magfield should serve")
parser.add_argument("device_ip", type=str, metavar="devip", help="Address of the STL source")
parser.add_argument("device_port", type=int, metavar="devport", help="Port of the STL source (default configuration of device is 21324)")

args = parser.parse_args()

log = Logger('magfield-stl')
log.set_logger_level(LogLevel.Info())
comm_channel = TcpCommunicationChannel(args.device_ip, args.device_port, log)
driver = DCS6K(comm_channel)
magfield = MagFieldImpl(driver)


async def do_loop():
    mqtt = MqttBridge(args.broker_ip, args.broker_port, args.device_id, magfield, log)
    mqtt.start_loop()
    while True:
        await asyncio.sleep(1)


asyncio.run(do_loop())
