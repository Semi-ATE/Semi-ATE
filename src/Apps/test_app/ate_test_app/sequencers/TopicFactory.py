from ate_test_app.sequencers.TheTestAppStatusAlive import TheTestAppStatusAlive
from typing import List, Optional

FRAMEWORK_VERSION = 1


class TopicFactory:

    def __init__(self, device_id: str, site_id: str):
        self._device_id = device_id
        self._site_id = site_id

    def master_status_topic(self):
        return f'ate/{self._device_id}/Master/status'

    def master_resource_topic(self, resource_id: Optional[str] = None):
        if resource_id is None:
            resource_id = '+'
        return f'ate/{self._device_id}/Master/peripherystate/{resource_id}'

    def generic_resource_response(self):
        # Evil hack: We want to see the responsetopics of all actuators here.
        return f'ate/{self._device_id}/Master/+/response'

    def control_status_topic(self):
        return f'ate/{self._device_id}/ControlApp/status/site{self._site_id}'

    def test_status_topic(self):
        return f'ate/{self._device_id}/TestApp/status/site{self._site_id}'

    def test_cmd_topic(self):
        return f'ate/{self._device_id}/TestApp/cmd'

    def test_result_topic(self):
        return f'ate/{self._device_id}/TestApp/testresult/site{self._site_id}'

    def tests_summary_topic(self):
        return f'ate/{self._device_id}/TestApp/testsummary/site{self._site_id}'

    def test_stdf_topic(self):
        return f'ate/{self._device_id}/TestApp/stdf/site{self._site_id}'

    def test_resource_topic(self, resource_id: str):
        return f'ate/{self._device_id}/TestApp/peripherystate/{resource_id}/site{self._site_id}/request'

    def test_log_topic(self):
        return f'ate/{self._device_id}/TestApp/log/site{self._site_id}'

    def test_execution_strategy_topic(self):
        return f'ate/{self._device_id}/TestApp/execution_strategy/site{self._site_id}'

    @staticmethod
    def test_execution_strategy_payload(execution_strategy: List[List[str]]):
        return {
            "type": "execution_strategy",
            "payload": execution_strategy
        }

    @staticmethod
    def test_status_payload(alive: TheTestAppStatusAlive):
        return {
            "type": "status",
            "framework_version": FRAMEWORK_VERSION,
            "test_version": "N/A",
            "payload": {"state": alive.value}
        }

    @staticmethod
    def test_result_payload(testdata: object):
        return {
            "type": "testresult",
            "payload": testdata
        }

    @staticmethod
    def test_resource_payload(resource_id: str, config: dict) -> dict:
        return {
            "type": "resource-config-request",
            "resource_id": resource_id,
            "config": config
        }

    @staticmethod
    def test_log_payload(testdata: str):
        return {
            "type": "log",
            "payload": testdata
        }

    @property
    def site_id(self):
        return self._site_id

    @property
    def mqtt_client_id(self):
        return f'testapp.{self._device_id}.{self._site_id}'
