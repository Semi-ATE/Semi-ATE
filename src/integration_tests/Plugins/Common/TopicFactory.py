from utils import GPIOState


class TopicFactory:
    @staticmethod
    def tester_status_topic(client_id: str):
        return f'ate/Tester/{client_id}/status'

    @staticmethod
    def tester_request_topic(client_id: str):
        return f'ate/Tester/{client_id}/test-request'

    @staticmethod
    def tester_test_done_topic(client_id: str):
        return f'ate/Tester/{client_id}/test-done'

    @staticmethod
    def tester_release_topic(tester_name):
        return f'ate/Tester/{tester_name}/test-release'

    @staticmethod
    def master_subscription_topic():
        return 'ate/Tester/+/test-request'

    @staticmethod
    def tester_terminate_topic():
        return 'ate/SCT-81-1F/TestApp/cmd'

    @staticmethod
    def _generate_message(type, payload):
        return {"type": type, "payload": payload}

    def tester_release_message(self, site: str) -> dict:
        return self._generate_message("test-release", {"site": site})

    def tester_request_message(self, site_id: str, state: GPIOState) -> dict:
        return self._generate_message("test-request", {"site": site_id, "state": state})

    def tester_status_message(self, status: str) -> dict:
        return self._generate_message("test-release", {"status": status})
