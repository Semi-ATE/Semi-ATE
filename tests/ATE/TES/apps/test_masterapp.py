import pytest
import mock
from ATE.TES.apps.masterApp import master_application
from ATE.TES.apps.masterApp import master_connection_handler


class TestApplication:

    def default_configuration(self):
        return {'broker_host': '192.168.0.1',
                'broker_port': '8991',
                'sites': ["0", "1"],
                'device_id': 'd',
                'jobsource': 'static',
                'jobformat': 'xml.micronas',
                'enable_timeouts': True,
                'skip_jobdata_verification': False,
                'environment': "abs",
                "user_settings_filepath": "master_user_settings.json"}

    def trigger_control_state_change(self, app: master_application.MasterApplication, site: str, newstate: str):
        app.on_control_status_changed(site, {"state": newstate, "interface_version": 1})

    def trigger_test_state_change(self, app: master_application.MasterApplication, site: str, newstate: str):
        app.on_testapp_status_changed(site, {"state": newstate, "interface_version": 1})

    def trigger_test_result_change(self, app: master_application.MasterApplication, site: str):
        app.on_testapp_testresult_changed(site, {"type": 'testresult', "payload": []})

    def test_masterapp_missed_broker_field_configuration(self):
        cfg = self.default_configuration()
        cfg.pop("broker_host")
        with pytest.raises(SystemExit):
            with pytest.raises(KeyError):
                _ = master_application.MasterApplication(cfg)

    def trigger_test_resource_change(self, app: master_application.MasterApplication, site: str, request_default_config: bool):
        custom_config = {
            'resource_id': 'unittest-dummy-resource-id',
            'config': {
                'dummy-param': 'dummy-value'
            }
        }
        default_config: dict = {}

        app.on_testapp_resource_changed(site, default_config if request_default_config else custom_config)

    def test_masterapp_correct_number_of_sites_triggers_initialized(self):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        print(app)
        assert(app.state == 'connecting')
        self.trigger_control_state_change(app, "0", "idle")
        assert(app.state == 'connecting')
        self.trigger_control_state_change(app, "1", "idle")
        assert(app.state == 'initialized')

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_load_test_to_all_sites")
    def test_masterapp_loadlot_triggers_load_commands(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        assert(app.state == 'initialized')
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        master_connection_handler.MasterConnectionHandler.send_load_test_to_all_sites.assert_called_once()

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_load_test_to_all_sites")
    def test_masterapp_siteloadcomplete_triggers_ready(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        assert(app.state == 'initialized')
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)

        self.trigger_control_state_change(app, "1", "loading")
        self.trigger_control_state_change(app, "0", "loading")

        assert(app.state == "loading")
        self.trigger_control_state_change(app, "0", "busy")
        assert(app.state == "loading")
        self.trigger_test_state_change(app, "0", "idle")

        self.trigger_control_state_change(app, "1", "busy")
        assert(app.state == "loading")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "ready")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_next_to_all_sites")
    def test_masterapp_next_triggers_test(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        assert(app.state == "ready")
        app.next(None)
        assert(app.external_state == "testing")
        master_connection_handler.MasterConnectionHandler.send_next_to_all_sites.assert_called_once()

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testsdone_triggers_ready(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.next(None)
        assert(app.external_state == "testing")
        self.trigger_test_state_change(app, "0", "testing")
        self.trigger_test_state_change(app, "1", "testing")

        self.trigger_test_state_change(app, "1", "idle")
        assert(app.external_state == "testing")
        self.trigger_test_result_change(app, "0")
        assert(app.external_state == "testing")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.external_state == "testing")
        self.trigger_test_result_change(app, "1")
        assert(app.state == "ready")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def test_masterapp_crash_triggers_error(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.testapp_disconnected(1, None)
        assert(app.state == "softerror")

    def test_masterapp_no_sites_configured_triggers_error(self):
        cfg = self.default_configuration()
        cfg['sites'] = []
        with pytest.raises(SystemExit):
            _ = master_application.MasterApplication(cfg)

    def test_masterapp_site_with_bad_interfaceversion_connects_triggers_error(self):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.on_control_status_changed("0", {"state": "idle", "interface_version": 120})
        assert (app.state == "error")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testresult_accepted_if_testing(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.next(None)
        assert(app.external_state == "testing")
        self.trigger_test_state_change(app, "0", "testing")
        self.trigger_test_state_change(app, "1", "testing")

        self.trigger_test_result_change(app, "0")
        self.trigger_test_result_change(app, "1")

        self.trigger_test_state_change(app, "1", "idle")
        assert(app.external_state == "testing")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "ready")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testresult_triggers_error_if_not_sent_during_test(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.on_testapp_testresult_changed("0", None)
        assert(app.state == "softerror")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def test_masterapp_error_state_testapp_crash(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.on_testapp_testresult_changed("0", None)
        self.trigger_test_state_change(app, "0", "crash")
        assert(app.state == "softerror")
        cmd = {'command': 'reset'}
        app.reset(cmd)
        assert(app.state == "connecting")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
        'XML': ''                                                                 # optional/unused for now
    })
    def _common_setup_for_testing_with_resource_synchronization(self, app, mocker, mock1):
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': 306426.001}
        app.load_command(cmd)
        app.all_siteloads_complete()

        app.next(None)
        assert(app.external_state == "testing")
        assert(app.state == "testing_inprogress")

        self.trigger_test_state_change(app, "0", "testing")
        self.trigger_test_state_change(app, "1", "testing")

        assert(app.state == "testing_inprogress")

        mocker.patch.object(app, 'apply_resource_config')

    def _trigger_resource_config_applied_callback(self, app):
        # when all active sites are waiting for the resource, app.apply_resource_config must be called,
        # which in turn calls the passed callback in (second argument) when the resource is actually configured.
        app.apply_resource_config.assert_called_once()
        callback = app.apply_resource_config.call_args[0][1]
        callback()  # currently we could directly call app._on_resource_config_applied() instead

    def test_masterapp_testing_both_sites_request_resources(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        # both sites request a non-default resource config and continue testing afterwards (using that resource)
        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        # both sites are now finished with the resource and request the default config
        mocker.patch.object(app, 'apply_resource_config')

        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        # now both sites continue testing until they are done

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_inprogress")
        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "ready")

    def test_masterapp_testing_first_site_completes_before_other_site_requests_resource(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "ready")

    def test_masterapp_testing_first_site_requests_resource_before_other_site_completes(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_waiting_for_resource")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "ready")

    def test_masterapp_testing_site_completes_while_waiting_for_resource(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "ready")

    def test_masterapp_testing_site_completes_while_waiting_for_resource_other_order(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_waiting_for_resource")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "testing_waiting_for_resource")

        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "testing_inprogress")

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_inprogress")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "ready")

    
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_masterapp_testing_all_sites_complete_while_waiting_for_resource(self, mocker):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)

        self._common_setup_for_testing_with_resource_synchronization(app, mocker)

        self.trigger_test_resource_change(app, "0", request_default_config=False)
        assert(app.state == "testing_inprogress")

        app.apply_resource_config.assert_not_called()

        self.trigger_test_resource_change(app, "1", request_default_config=False)
        assert(app.state == "testing_waiting_for_resource")

        self.trigger_test_result_change(app, "1")
        assert(app.state == "testing_waiting_for_resource")
        self.trigger_test_state_change(app, "1", "idle")
        assert(app.state == "testing_waiting_for_resource")

        self.trigger_test_result_change(app, "0")
        assert(app.state == "testing_waiting_for_resource")
        self.trigger_test_state_change(app, "0", "idle")
        assert(app.state == "ready")

        # TODO: the callback should probably be canceled eventually, for now we just check that it doesn't cause an error
        self._trigger_resource_config_applied_callback(app)
        assert(app.state == "ready")
