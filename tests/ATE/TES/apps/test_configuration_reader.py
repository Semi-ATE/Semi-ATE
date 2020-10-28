import pytest
import json
from ATE.Tester.TES.apps.common.configuration_reader import ConfigReader


CONFIG_FILE_PATH = "./tests/ATE/TES/apps/config_file_test.json"
CONFIG_FILE_PATH_USER = "./tests/ATE/TES/apps/config_file_test_partial_user.json"
CONFIG_FILE_PATH_BAD = "./tests/ATE/TES/apps/config_file_test_bad.json"


class TestConfigReader:

    def test_read_configuration_file_correct_config(self):
        configuration = ConfigReader(CONFIG_FILE_PATH)
        assert (configuration.get_configuration() == {"broker_host": "127.0.0.1",
                                                      "broker_port": 1883,
                                                      "site_id": "0",
                                                      "device_id": "device-id"})

    def test_read_configuration_file_correct_config_user(self):
        configuration = ConfigReader(CONFIG_FILE_PATH_USER)
        assert (configuration.get_configuration() == {"device_id": "users_device",
                                                      "site_id": "1",
                                                      "previously_not_existing_key": "value"})

    def test_read_configuration_file_with_user_dict(self):
        user_config_dict = {"broker_host": "127.0.0.1", "site_id": "2"}

        configuration = ConfigReader(CONFIG_FILE_PATH)
        assert (configuration.get_configuration_ex(
            user_config_dict=user_config_dict) == {"broker_host": "127.0.0.1",
                                                   "broker_port": 1883,
                                                   "site_id": "2",
                                                   "device_id": "device-id"})

    def test_read_configuration_file_with_user_file(self):
        user_config_dict = {"broker_host": "127.0.0.1", "site_id": "2"}

        configuration = ConfigReader(CONFIG_FILE_PATH)
        assert (configuration.get_configuration_ex(
            user_config_file=CONFIG_FILE_PATH_USER,
            user_config_dict=user_config_dict) == {"broker_host": "127.0.0.1",
                                                   "broker_port": 1883,
                                                   "site_id": "2",
                                                   "device_id": "users_device",
                                                   "previously_not_existing_key": "value"})

    def test_read_configuration_file_wrong_path(self):
        configuration = ConfigReader("")
        with pytest.raises(FileNotFoundError):
            configuration.get_configuration()

    def test_read_configuration_file_wrong_file_format(self):
        configuration = ConfigReader(CONFIG_FILE_PATH_BAD)
        with pytest.raises(json.JSONDecodeError):
            configuration.get_configuration()

    def test_read_configuration_with_None_file_raises_error(self):
        configuration = ConfigReader(None)
        with pytest.raises(TypeError):
            configuration.get_configuration()

    def test_read_configuration_ex_with_None_file_is_ok(self):
        configuration = ConfigReader(None)
        assert configuration.get_configuration_ex() == {}
