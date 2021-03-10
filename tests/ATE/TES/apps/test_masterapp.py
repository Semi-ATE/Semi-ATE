import pytest
import mock
import os
from utils import (create_xml_file, DEVICE_ID)
from ATE.Tester.TES.apps.masterApp import master_application
from ATE.Tester.TES.apps.masterApp import master_connection_handler
from ATE.Tester.TES.apps.masterApp.utils.yield_information import YieldInformationHandler

LOT_NUMBER = '306426.001'
FILE_PATH = os.path.dirname(__file__)

XML_PATH = os.path.join(FILE_PATH, 'le306426001_template.xml')
XML_PATH_NEW = os.path.join(FILE_PATH, 'le306426001.xml')

# this will generate the desired xml file and must be called before running the tests
create_xml_file(XML_PATH, XML_PATH_NEW, DEVICE_ID)


class TestApplication:

    def default_configuration(self):
        return {'broker_host': '192.168.0.1',
                'broker_port': '8991',
                'sites': ["0", "1"],
                'device_id': DEVICE_ID,
                'jobsource': 'filesystem',
                'jobformat': 'xml.micronas',
                "filesystemdatasource.path": FILE_PATH,
                "filesystemdatasource.jobpattern": "le306426001.xml",
                'enable_timeouts': True,
                'skip_jobdata_verification': False,
                'environment': "abs",
                'Handler': "HTO92-20F",
                "user_settings_filepath": "master_user_settings.json"}

    def trigger_control_state_change(self, app: master_application.MasterApplication, site: str, newstate: str):
        app.on_control_status_changed(site, {"type": "status", "payload": {"state": newstate}, "interface_version": 1})

    def trigger_test_state_change(self, app: master_application.MasterApplication, site: str, newstate: str):
        app.on_testapp_status_changed(site, {"type": "status", "payload": {"state": newstate}, "interface_version": 1})

    @mock.patch.object(YieldInformationHandler, 'extract_yield_information', return_value=(True, ''))
    def trigger_test_result_change(self, app: master_application.MasterApplication, site: str, mocker):
        app.on_testapp_testresult_changed(site, {"type": 'testresult', "payload":
                                                 [{'type': 'PIR', 'REC_LEN': None, 'REC_TYP': 5, 'REC_SUB': 10, 'HEAD_NUM': 0, 'SITE_NUM': 0},
                                                  {'type': 'PTR', 'REC_LEN': None, 'REC_TYP': 15, 'REC_SUB': 10, 'TEST_NUM': 1, 'HEAD_NUM': 0, 'SITE_NUM': 0, 'TEST_FLG': 0, 'PARM_FLG': 0, 'RESULT': 3.0, 'TEST_TXT': 'sfg_1.new_parameter1', 'ALARM_ID': '', 'OPT_FLAG': 2, 'RES_SCAL': 0, 'LLM_SCAL': 0, 'HLM_SCAL': 0, 'LO_LIMIT': 3.0, 'HI_LIMIT': 5.0, 'UNITS': '', 'C_RESFMT': '%7.3f', 'C_LLMFMT': '%7.3f', 'C_HLMFMT': '%7.3f', 'LO_SPEC': -2, 'HI_SPEC': 4},
                                                  {'type': 'FTR', 'REC_LEN': None, 'REC_TYP': 15, 'REC_SUB': 20, 'TEST_NUM': 1, 'HEAD_NUM': 0, 'SITE_NUM': 0, 'TEST_FLG': 1, 'OPT_FLAG': 255, 'CYCL_CNT': None, 'REL_VADR': None, 'REPT_CNT': None, 'NUM_FAIL': None, 'XFAIL_AD': None, 'YFAIL_AD': None, 'VECT_OFF': None, 'RTN_ICNT': 0, 'PGM_ICNT': 0, 'RTN_INDX': None, 'RTN_STAT': None, 'PGM_INDX': None, 'PGM_STAT': None, 'FAIL_PIN': None, 'VECT_NAM': None, 'TIME_SET': None, 'OP_CODE': None, 'TEST_TXT': None, 'ALARM_ID': None, 'PROG_TXT': None, 'RSLT_TXT': None, 'PATG_NUM': None, 'SPIN_MAP': None},
                                                  {'type': 'PRR', 'REC_LEN': None, 'REC_TYP': 5, 'REC_SUB': 20, 'HEAD_NUM': 0, 'SITE_NUM': 0, 'PART_FLG': 0, 'NUM_TEST': 1, 'HARD_BIN': 1, 'SOFT_BIN': 1, 'X_COORD': 1, 'Y_COORD': 1, 'TEST_T': 0, 'PART_ID': '1', 'PART_TXT': '1', 'PART_FIX': 0}]})

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
        assert(app.state == 'connecting')
        self.trigger_control_state_change(app, "0", "idle")
        assert(app.state == 'connecting')
        self.trigger_control_state_change(app, "1", "idle")
        assert(app.state == 'initialized')

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_load_test_to_all_sites")
    def test_masterapp_loadlot_triggers_load_commands(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        assert(app.state == 'initialized')
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
        app.load_command(cmd)
        master_connection_handler.MasterConnectionHandler.send_load_test_to_all_sites.assert_called_once()

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_load_test_to_all_sites")
    def test_masterapp_siteloadcomplete_triggers_ready(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        assert(app.state == 'initialized')
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    @mock.patch.object(master_connection_handler.MasterConnectionHandler, "send_next_to_all_sites")
    def test_masterapp_next_triggers_test(self, mock1, mock2):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
        app.load_command(cmd)
        app.all_siteloads_complete()
        assert(app.state == "ready")
        app.next(None)
        assert(app.external_state == "testing")
        master_connection_handler.MasterConnectionHandler.send_next_to_all_sites.assert_called_once()

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testsdone_triggers_ready(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def test_masterapp_crash_triggers_error(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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
        app.on_control_status_changed("0", {"type": "status", "payload": {"state": "idle"}, "interface_version": 120})
        assert (app.state == "error")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testresult_accepted_if_testing(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def test_masterapp_testresult_triggers_error_if_not_sent_during_test(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
        app.load_command(cmd)
        app.all_siteloads_complete()
        app.on_testapp_testresult_changed("0", None)
        assert(app.state == "softerror")

    @mock.patch.object(master_application.MasterApplication, 'get_test_parameters', return_value={
        'testapp_script_path': './thetest_application.py',                  # required
        'cwd': 'src/ATE/apps/testApp',     # optional
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def test_masterapp_error_state_testapp_crash(self, mock1):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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
        'testapp_script_args': ['--verbose'],
        'bin_table': ''                                                                 # optional/unused for now
    })
    def _common_setup_for_testing_with_resource_synchronization(self, app, mocker, mock1):
        app.startup_done()
        app.all_sites_detected()
        cmd = {'command': 'load', 'lot_number': LOT_NUMBER}
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

    @staticmethod
    def _generate_PRR(part_id, sbin):
        from Semi_ATE.STDF import PRR
        endian = '<'
        version = 'V4'
        rec = PRR(version, endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)
        rec.set_value('PART_FLG', ['0', '0', '0', '0', '1', '0', '0', '0'])
        rec.set_value('NUM_TEST', 0)
        rec.set_value('HARD_BIN', 0)
        rec.set_value('SOFT_BIN', sbin)
        rec.set_value('PART_ID', part_id)
        return rec.to_dict()

    @staticmethod
    def get_bin_settings():
        return [{'SBIN': '1', 'HBIN': '1', 'SBINNAME': 'SB_GOOD1', 'GROUP': 'type1', 'DESCRIPTION': 'Our best choice'},
                {'SBIN': '2', 'HBIN': '1', 'SBINNAME': 'SB_CONT_OPEN', 'GROUP': 'type1', 'DESCRIPTION': 'Open Contacts'},
                {'SBIN': '4', 'HBIN': '1', 'SBINNAME': 'SB_CONT_OPEN', 'GROUP': 'type2', 'DESCRIPTION': 'Open Contacts'},
                {'SBIN': '3', 'HBIN': '1', 'SBINNAME': 'SB_FAILED', 'GROUP': 'type1', 'DESCRIPTION': ' SMU Warning'}]

    def test_masterapp_testing_yield_generation(self):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        bin_settings = self.get_bin_settings()
        app._result_info_handler.set_bin_settings(bin_settings)

        prr = self._generate_PRR('abc', 1)
        app._result_info_handler.handle_result(prr)

        prr = self._generate_PRR('eft', 2)
        app._result_info_handler.handle_result(prr)

        prr = self._generate_PRR('zzz', 4)
        app._result_info_handler.handle_result(prr)

        site_num = str(prr['SITE_NUM'])
        site_yield_info = app._result_info_handler.get_site_yield_info_message(site_num)

        assert site_yield_info == [{'name': 'type1', 'value': 66.66666666666666, 'count': 2, 'siteid': site_num},
                                   {'name': 'type2', 'value': 33.33333333333333, 'count': 1, 'siteid': site_num},
                                   {'name': 'sum', 'value': 100.0, 'count': 3, 'siteid': site_num},
                                   ]

        yield_info = app._result_info_handler.get_yield_messages()
        all_site_num = '-1'
        assert yield_info == [{'name': 'type1', 'value': 66.66666666666666, 'count': 2, 'siteid': site_num},
                              {'name': 'type2', 'value': 33.33333333333333, 'count': 1, 'siteid': site_num},
                              {'name': 'sum', 'value': 100.0, 'count': 3, 'siteid': site_num},
                              {'name': 'type1', 'value': 66.66666666666666, 'count': 2, 'siteid': all_site_num},
                              {'name': 'type2', 'value': 33.33333333333333, 'count': 1, 'siteid': all_site_num},
                              {'name': 'sum', 'value': 100.0, 'count': 3, 'siteid': all_site_num},
                              ]

    def test_masterapp_testing_yield_generation_override_part_id(self):
        cfg = self.default_configuration()
        app = master_application.MasterApplication(cfg)
        bin_settings = self.get_bin_settings()
        app._result_info_handler.set_bin_settings(bin_settings)

        prr = self._generate_PRR('abc', 1)
        app._result_info_handler.handle_result(prr)
        site_num = str(prr['SITE_NUM'])

        site_yield_info = app._result_info_handler.get_site_yield_info_message(site_num)

        assert site_yield_info == [{'name': 'type1', 'value': 100.0, 'count': 1, 'siteid': site_num},
                                   {'name': 'type2', 'value': 0.0, 'count': 0, 'siteid': site_num},
                                   {'name': 'sum', 'value': 100.0, 'count': 1, 'siteid': site_num},
                                   ]

        prr = self._generate_PRR('abc', 4)
        app._result_info_handler.handle_result(prr)

        site_num = str(prr['SITE_NUM'])
        site_yield_info = app._result_info_handler.get_site_yield_info_message(site_num)
        assert site_yield_info == [{'name': 'type1', 'value': 0.00, 'count': 0, 'siteid': site_num},
                                   {'name': 'type2', 'value': 100.00, 'count': 1, 'siteid': site_num},
                                   {'name': 'sum', 'value': 100.00, 'count': 1, 'siteid': site_num},
                                   ]
