from ate_common.logger import Logger
from ate_semiateplugins.hookspec import hookimpl

from semi_ate_msct.tester.tester import Tester
from semi_ate_msct.flatcache import flatcache


__version__ = '0.0.0'


class BusinessObjectStandin:
    def __init__(self, logger=None):
        self.logger = logger

    def do_import(self):
        print('do_import')
        return False

    def do_export(self):
        print('do_export')
        return False

    def get_abort_reason(self):
        return "This is a standin object from MiniSCT without functionality"

    def set_mqtt_client(self, mqtt):
        print('set_mqtt_client')
        pass

    def set_configuration_values(data):
        print('set_configuration_values')
        pass

    def apply_configuration(self, data):
        print("Configuration applied.")


class Plugin:
    

    @staticmethod
    def prefix():
        return 'semi-ate-msct'

    @hookimpl
    def get_plugin_identification():
        return {
            "Name": f"{Plugin.prefix()} MiniSCT Plugin",
            "Version": "0.0"
        }

    @hookimpl
    def get_importer_names():
        return []

    @hookimpl
    def get_exporter_names():
        return [
            {"display_name": f"{Plugin.prefix()} Dummy Exporter",
             "version": __version__,
             "name": f"{Plugin.prefix()} Dummy Exporter"}]

    @hookimpl
    def get_equipment_names():
        return [
            {"display_name": "Dummy Equipment",
             "version": __version__,
             "name": f"{Plugin.prefix()} DummyEquipment"}]

    @hookimpl
    def get_devicepin_importer_names():
        return [
             {"display_name": f"{Plugin.prefix()} Dummy Pinimport",
              "version": __version__,
              "name": f"{Plugin.prefix()} Dummy Pinimport"}]

    @hookimpl
    def get_instrument_names():
        return [
            # {"display_name": f"{Plugin.prefix()} Dummy Instrument",
            #  "version": __version__,
            #  "manufacturer": "Semi-ATE",
            #  "name": f"{Plugin.prefix()}.Instrument"}
            ]

    @hookimpl
    def get_tester_names():
        return [
            {
                #"display_name": f"{Plugin.prefix()} Mini-SCT",
                "display_name": f"Mini-SCT V{__version__}",
                "version": __version__,
                "manufacturer": "Semi-ATE",
                "name": f"{Plugin.prefix()} Mini-SCT"
            }
        ]

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": f"{Plugin.prefix()} Flatcache [Catflache]",
             "version": __version__,
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
            print('MiniSCT.get_equipment')
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
        if tester_name == f"{Plugin.prefix()} Mini-SCT":
            return Tester()

    @hookimpl
    def get_general_purpose_function(func_name: str, logger: Logger):
        print(f"Get General Purpose Function: {func_name}")
        if func_name == f"{Plugin.prefix()} Flatcache":
            return flatcache.Flatcache()

    @hookimpl
    def get_configuration_options(object_name):
        if object_name == f"{Plugin.prefix()} Flatcache":
            return ["ip", "port"]

