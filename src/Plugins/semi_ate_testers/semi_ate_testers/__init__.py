from ate_common.logger import Logger
from ate_semiateplugins.hookspec import hookimpl

from semi_ate_testers.master_testers.dummy_master_single_tester import DummyMasterSingleTester
from semi_ate_testers.master_testers.dummy_master_parallel_tester import DummyMasterParallelTester
from semi_ate_testers.Flatcache import Flatcache
from semi_ate_testers.testers.dummy_single_tester import DummySingleTester
from semi_ate_testers.testers.dummy_parallel_tester import DummyParallelTester

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

    @staticmethod
    def prefix():
        return 'Semi_ATE'

    @hookimpl
    def get_plugin_identification():
        return {
            "Name": f"{Plugin.prefix()} Tester Reference Plugin",
            "Version": "0.01"
        }

    @hookimpl
    def get_importer_names():
        return []

    @hookimpl
    def get_exporter_names():
        return [
            {"display_name": f"{Plugin.prefix()} Dummy Exporter",
             "version": "0.0",
             "name": f"{Plugin.prefix()} Dummy Exporter"}]

    @hookimpl
    def get_equipment_names():
        return [
            {"display_name": f"{Plugin.prefix()} Dummy Equipment",
             "version": "0.0",
             "name": f"{Plugin.prefix()} Dummy Equipment"}]

    @hookimpl
    def get_devicepin_importer_names():
        return [
            {"display_name": f"{Plugin.prefix()} Dummy Pinimport",
             "version": "0.0",
             "name": f"{Plugin.prefix()} Dummy Pinimport"}]

    @hookimpl
    def get_instrument_names():
        return [
            {"display_name": f"{Plugin.prefix()} Dummy Instrument",
             "version": "0.0",
             "manufacturer": "ACME International",
             "name": f"{Plugin.prefix()} Dummy Instrument"}]

    @hookimpl
    def get_tester_names():
        return [
            {
                "display_name": f"{Plugin.prefix()} Single Tester",
                "version": "0.0",
                "manufacturer": "Semi-ATE",
                "name": f"{Plugin.prefix()} Single Tester"
            },
            {
                "display_name": f"{Plugin.prefix()} Parallel Tester",
                "version": "0.0",
                "manufacturer": "Semi-ATE",
                "name": f"{Plugin.prefix()} Parallel Tester"
            },
            {
                "display_name": f"{Plugin.prefix()} Mini-SCT ",
                "version": "0.0",
                "manufacturer": "Semi-ATE",
                "name": f"{Plugin.prefix()} Mini-SCT"
            },
            {
                "display_name": f"{Plugin.prefix()} Dummy Mini-SCT ",
                "version": "0.0",
                "manufacturer": "Semi-ATE",
                "name": f"{Plugin.prefix()} Dummny Mini-SCT"
            }
        ]

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": f"{Plugin.prefix()} Flatcache [Catflache]",
             "version": "0.0",
             "manufacturer": "Semi-ATE",
             "name": f"{Plugin.prefix()} Flatcache"}]

    @hookimpl
    def get_importer(importer_name):
        if Plugin.prefix() in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_exporter(exporter_name):
        if Plugin.prefix() in exporter_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_equipment(equipment_name):
        if Plugin.prefix() in equipment_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_devicepin_importer(importer_name):
        if Plugin.prefix() in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_instrument(instrument_name: str, logger: Logger):
        if Plugin.prefix() in instrument_name:
            return BusinessObjectStandin(logger)

    @hookimpl
    def get_instrument_proxy(instrument_name):
        if Plugin.prefix() in instrument_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_tester(tester_name: str):
        if tester_name == f"{Plugin.prefix()} Single Tester":
            return DummySingleTester()
        elif tester_name == f"{Plugin.prefix()} Parallel Tester":
            return DummyParallelTester()
        elif tester_name == f"{Plugin.prefix()} Mini-SCT":
            import platform
            # Tester package for minisct hardware is not available on windows
            if "linux" in platform.system().lower() and "aarch64" in platform.machine().lower():
                from semi_ate_testers.testers.minisct import MiniSCT
                return MiniSCT()
            else:
                from semi_ate_testers.testers.dummy_minisct import DummyMiniSCT
                return DummyMiniSCT()
        elif tester_name == f"{Plugin.prefix()} Dummny Mini-SCT":
            from semi_ate_testers.testers.dummy_minisct import DummyMiniSCT
            return DummyMiniSCT()

    @hookimpl
    def get_tester_master(tester_name: str):
        if tester_name == f"{Plugin.prefix()} Master Single Tester":
            return DummyMasterSingleTester()
        elif tester_name == f"{Plugin.prefix()} Master Parallel Tester":
            return DummyMasterParallelTester()

    @hookimpl
    def get_general_purpose_function(func_name: str, logger: Logger):
        print(f"Get General Purpose Function: {func_name}")
        if func_name == f"{Plugin.prefix()} Flatcache":
            return Flatcache.Flatcache()

    @hookimpl
    def get_configuration_options(object_name):
        if object_name == f"{Plugin.prefix()} Flatcache":
            return ["ip", "port"]

        if object_name == f"{Plugin.prefix()} Dummy Instrument":
            return ["ip", "port"]

__version__ = '0.0.0'
