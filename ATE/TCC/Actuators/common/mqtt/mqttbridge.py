from ATE.common.logger import LogLevel
import json
import aiomqtt


class MqttBridge:
    def __init__(self, broker_ip, broker_port, device_id, actuator_impl, log):
        self.actuator_type = actuator_impl.get_type()
        self.mqtt_client = aiomqtt.Client(client_id=f"{device_id}{self.actuator_type}")
        self.mqtt_client.reconnect_delay_set(10, 15)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.actuator_impl = actuator_impl
        self.host = broker_ip
        self.port = broker_port
        self.device_id = device_id
        self._log = log

    def start_loop(self):
        self.mqtt_client.will_set(f"ate/{self.device_id}/{self.actuator_type}/status", json.dumps({"status": "crash"}), 0, False)
        self.mqtt_client.connect_async(self.host, self.port)
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, conect_res):
        topic = f"ate/{self.device_id}/{self.actuator_type}/io-control/request"

        self.mqtt_client.subscribe(topic)
        self.post_status()
        self._log.log_message(LogLevel.Debug(), 'Connection established')

    def on_message(self, client, userdata, message):
        try:
            result = self.on_request(message.payload)
            result_json = json.dumps(result)
            self.mqtt_client.publish(f"ate/{self.device_id}/{self.actuator_type}/io-control/response", result_json)
        except json.JSONDecodeError as error:
            self._log.log_message(LogLevel.Error(), f'{error}')

    def on_disconnect(self, client, userdata, distc_res):
        self._log.log_message(LogLevel.Debug(), 'Disconnected')

    def post_status(self):
        message = {"status": self.actuator_impl.get_status()}
        self.mqtt_client.publish(f"ate/{self.device_id}/{self.actuator_type}/status", json.dumps(message))

    def on_request(self, request_data):
        request_dict = json.loads(request_data)
        ioctl = request_dict["ioctl_name"]
        params = request_dict["parameters"]
        if request_dict["type"] == "io-control-drycall":
            result = self.actuator_impl.do_dry_call(ioctl, params)
            type = "io-drycall-response"
        else:
            result = self.actuator_impl.do_io_control(ioctl, params)
            type = "io-control-response"

        if result == {}:
            return {"type": type, "ioctl_name": ioctl, "result": "bad_ioctl", "error_message": "The provided controlcode is unknown."}
        return {"type": type, "ioctl_name": ioctl, "result": result}
