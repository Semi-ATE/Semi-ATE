from ate_common.logger import Logger
from ate_semiateplugins.hookspec import hookimpl
from dummy_tester.testers.dummy_single_tester import DummySingleTester
from dummy_tester.testers.dummy_parallel_tester import DummyParallelTester
from dummy_tester.master_testers.dummy_master_single_tester import DummyMasterSingleTester
from dummy_tester.master_testers.dummy_master_parallel_tester import DummyMasterParallelTester


class BusinessObjectStandin:
    def __init__(self, logger: Logger = None):
        self.logger = logger

    def do_import(self):
        return False

    def do_export(self):
        return False

    def get_abort_reason(self):
        return "This is a standin object without functionality"

    def set_mqtt_client(self, mqtt):
        pass

    def set_configuration_values(data):
        pass

    def apply_configuration(self, data):
        print("Configuration applied.")


class Plugin:

    @hookimpl
    def get_plugin_identification():
        return {
            "Name": "Dummy.Plugin Reference Plugin",
            "Version": "0.01"
        }

    @hookimpl
    def get_importer_names():
        return []

    @hookimpl
    def get_exporter_names():
        return [
            {"display_name": "Dummy Exporter",
             "version": "0.0",
             "name": "DummyTester.DummyExporter"}]

    @hookimpl
    def get_equipment_names():
        return [
            {"display_name": "Dummy Equipment",
             "version": "0.0",
             "name": "DummyTester.DummyEquipment"}]

    @hookimpl
    def get_devicepin_importer_names():
        return [
            {"display_name": "Dummy Pinimport",
             "version": "0.0",
             "name": "DummyTester.DummyPinimport"}]

    @hookimpl
    def get_instrument_names():
        return [
            {"display_name": "Dummy Instrument",
             "version": "0.0",
             "manufacturer": "ACME International",
             "name": "DummyTester.DummyInstrument"}]

    @hookimpl
    def get_tester_names():
        return [
            {"display_name": "Dummy Single Tester",
             "version": "0.0",
             "manufacturer": "Dummy Company",
             "name": "DummySingleTester"},
            {"display_name": "Dummy Parallel Tester",
             "version": "0.0",
             "manufacturer": "Dummy Company",
             "name": "DummyParallelTester"}]

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": "Flatcache [Catflache]",
             "version": "0.0",
             "manufacturer": "Dummy Company",
             "name": "DummyTester.Flatcache"}]

    @hookimpl
    def get_importer(importer_name):
        if "DummyTester." in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_exporter(exporter_name):
        if "DummyTester." in exporter_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_equipment(equipment_name):
        if "DummyTester." in equipment_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_devicepin_importer(importer_name):
        if "DummyTester." in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_instrument(instrument_name: str, logger: Logger):
        if "DummyTester." in instrument_name:
            return BusinessObjectStandin(logger)

    @hookimpl
    def get_instrument_proxy(instrument_name):
        if "DummyTester." in instrument_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_tester(tester_name: str):
        if tester_name == "DummySingleTester":
            return DummySingleTester()
        elif tester_name == "DummyParallelTester":
            return DummyParallelTester()

    @hookimpl
    def get_tester_master(tester_name: str):
        if tester_name == "DummyMasterSingleTester":
            return DummyMasterSingleTester()
        elif tester_name == "DummyMasterParallelTester":
            return DummyMasterParallelTester()

    @hookimpl
    def get_general_purpose_function(func_name: str, logger: Logger):
        if "DummyTester." in func_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_configuration_options(object_name):
        if "DummyTester." in object_name:
            return BusinessObjectStandin()
__version__ = '0.0.0'
