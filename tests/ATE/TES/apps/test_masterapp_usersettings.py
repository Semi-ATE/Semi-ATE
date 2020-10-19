from ATE.Tester.TES.apps.masterApp import master_application
from ATE.Tester.TES.apps.masterApp.user_settings import UserSettings


DEFAULT_USER_SETTINGS_FILE_UNITTEST = 'master_user_settings_from_unittest.json'


class TestApplication:

    def default_configuration(self):
        return {'broker_host': '192.168.0.1',
                'broker_port': '8991',
                'sites': ["0", "1"],
                'device_id': 'd',
                'jobsource': 'static',
                'jobformat': 'xml.micronas',
                'enable_timeouts': True,
                'Handler': "abc",
                'environment': "abs"}

    def default_configuration_with_persistent_user_settings(self):
        cfg = self.default_configuration()
        cfg['user_settings_filepath'] = DEFAULT_USER_SETTINGS_FILE_UNITTEST
        return cfg

    def default_UserSettings(self):
        return UserSettings.get_defaults()

    def customized_UserSettings(self):
        return [{'name': 'stop_on_fail',
                 'active': True,
                 'value': -1},
                ]

    def test_masterapp_usersettings_persistent_config_disabled_without_filepath(self, mocker):
        mocker.patch.object(UserSettings, 'save_to_file')
        mocker.patch.object(UserSettings, 'load_from_file')

        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        assert app.persistent_user_settings_enabled is False
        assert app.user_settings_filepath is None
        assert app.user_settings == self.default_UserSettings()

        UserSettings.save_to_file.assert_not_called()
        UserSettings.load_from_file.assert_not_called()

    def test_masterapp_usersettings_persistent_config_default_initialized_if_file_not_exists(self, mocker):
        mocker.patch.object(UserSettings, 'save_to_file')
        mocker.patch.object(UserSettings, 'load_from_file')
        UserSettings.load_from_file.side_effect = FileNotFoundError()

        cfg = self.default_configuration_with_persistent_user_settings()
        app = master_application.MasterApplication(cfg)

        assert app.persistent_user_settings_enabled is True
        assert app.user_settings_filepath is DEFAULT_USER_SETTINGS_FILE_UNITTEST
        assert app.user_settings == self.default_UserSettings()

        UserSettings.load_from_file.assert_called_once_with(DEFAULT_USER_SETTINGS_FILE_UNITTEST)
        UserSettings.save_to_file.assert_called_once_with(DEFAULT_USER_SETTINGS_FILE_UNITTEST, self.default_UserSettings(), add_defaults=mocker.ANY)

    def test_masterapp_usersettings_persistent_config_initialized_from_existing_file(self, mocker):
        mocker.patch.object(UserSettings, 'save_to_file')

        mocker.patch.object(UserSettings, 'load_from_file')
        custom_usersettings = self.default_UserSettings()  # UserSettings.load_from_file includes all default settings
        custom_usersettings.update(self.customized_UserSettings()[0])
        UserSettings.load_from_file.return_value = custom_usersettings

        cfg = self.default_configuration_with_persistent_user_settings()
        app = master_application.MasterApplication(cfg)

        assert app.persistent_user_settings_enabled is True
        assert app.user_settings_filepath is DEFAULT_USER_SETTINGS_FILE_UNITTEST
        assert app.user_settings == custom_usersettings

        UserSettings.load_from_file.assert_called_once_with(DEFAULT_USER_SETTINGS_FILE_UNITTEST)
        UserSettings.save_to_file.assert_called_once_with(DEFAULT_USER_SETTINGS_FILE_UNITTEST, custom_usersettings, add_defaults=True)

    def test_masterapp_usersettings_saved_on_modify(self, mocker):
        mocker.patch.object(UserSettings, 'save_to_file')  # mock to avoid file creation
        mocker.patch.object(UserSettings, 'load_from_file')
        UserSettings.load_from_file.side_effect = FileNotFoundError()

        cfg = self.default_configuration_with_persistent_user_settings()
        app = master_application.MasterApplication(cfg)

        assert app.user_settings == self.default_UserSettings()
        mocker.patch.object(UserSettings, 'save_to_file')  # reset Mocker to assert the call we are actually interested in

        app.modify_user_settings(self.customized_UserSettings())

        expected_usersettings = self.default_UserSettings()  # default settings will always be included
        expected_usersettings.update(app._extract_settings(self.customized_UserSettings()))
        for expected_usersetting in expected_usersettings:
            assert app.user_settings[expected_usersetting] == expected_usersettings[expected_usersetting]

        UserSettings.save_to_file.assert_called_once_with(DEFAULT_USER_SETTINGS_FILE_UNITTEST, expected_usersettings, add_defaults=True)
