from ATE.common.logger import Logger
from ATE.semiateplugins.hookspec import hookimpl
from TDKMicronas.Testers import MiniSCT, MaxiSCT
from TDKMicronas.Flatcache import Flatcache


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
            "Name": "TDK.Micronas Reference Plugin",
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
             "name": "TDKMicronas.DummyExporter"}]

    @hookimpl
    def get_equipment_names():
        return [
            {"display_name": "Dummy Equipment",
             "version": "0.0",
             "name": "TDKMicronas.DummyEquipment"}]

    @hookimpl
    def get_devicepin_importer_names():
        return [
            {"display_name": "Dummy Pinimport",
             "version": "0.0",
             "name": "TDKMicronas.DummyPinimport"}]

    @hookimpl
    def get_instrument_names():
        return [
            {"display_name": "Dummy Instrument",
             "version": "0.0",
             "manufacturer": "ACME International",
             "name": "TDKMicronas.DummyInstrument"}]

    @hookimpl
    def get_tester_names():
        return [
            {"display_name": "Mini SCT",
             "version": "0.0",
             "manufacturer": "TDK Micronas",
             "name": "TDKMicronas.MiniSCT"},
            {"display_name": "Maxi SCT",
             "version": "0.0",
             "manufacturer": "TDK Micronas",
             "name": "TDKMicronas.MaxiSCT"}]

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": "Flatcache [Catflache]",
             "version": "0.0",
             "manufacturer": "TDK Micronas",
             "name": "TDKMicronas.Flatcache"}]

    @hookimpl
    def get_importer(importer_name):
        if "TDKMicronas." in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_exporter(exporter_name):
        if "TDKMicronas." in exporter_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_equipment(equipment_name):
        if "TDKMicronas." in equipment_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_devicepin_importer(importer_name):
        if "TDKMicronas." in importer_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_instrument(instrument_name: str, logger: Logger):
        if "TDKMicronas." in instrument_name:
            return BusinessObjectStandin(logger)

    @hookimpl
    def get_instrument_proxy(instrument_name):
        if "TDKMicronas." in instrument_name:
            return BusinessObjectStandin()

    @hookimpl
    def get_tester(tester_name):
        if tester_name == "TDKMicronas.MiniSCT":
            return MiniSCT.MiniSCT()
        elif tester_name == "TDKMicronas.MaxiSCT":
            return MaxiSCT.MaxiSCT()

    @hookimpl
    def get_general_purpose_function(func_name: str, logger: Logger):
        print(f"Get General Purpose Function: {func_name}")
        if func_name == "TDKMicronas.Flatcache":
            return Flatcache.Flatcache()

    @hookimpl
    def get_configuration_options(object_name):
        if object_name == "TDKMicronas.Flatcache":
            return ["ip", "port"]

        if object_name == "TDKMicronas.DummyInstrument":
            return ["ip", "port"]
