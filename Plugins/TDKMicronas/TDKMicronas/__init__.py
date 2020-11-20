from ATE.semiateplugins.hookspec import hookimpl
from TDKMicronas.Testers import MiniSCT


class BusinessObjectStandin:
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


class Plugin:

    @hookimpl
    def get_plugin_identification():
        return {
            "Name": "TDK.Micronas Reference Plugin",
            "Version": "0.01"
        }

    @hookimpl
    def get_importer_names():
        return [
            {"display_name": "Dummy Importer",
             "version": "0.0",
             "name": "TDKMicronas.DummyImporter"}]

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
             "name": "TDKMicronas.DummyInstrument"},

            {"display_name": "Flux Compensator",
             "version": "0.0",
             "manufacturer": "ACME International",
             "name": "TDKMicronas.FluxCompensator"},

            {"display_name": "Blackhole Generator",
             "version": "0.0",
             "manufacturer": "CI Systems",
             "name": "TDKMicronas.BlackholeGen"}]

    @hookimpl
    def get_tester_names():
        return [
            {"display_name": "Mini SCT",
             "version": "0.0",
             "manufacturer": "TDK Micronas",
             "name": "TDKMicronas.MiniSCT"}]

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": "METIS Connector",
             "version": "0.0",
             "manufacturer": "TDK Micronas",
             "name": "TDKMicronas.Metis"}]

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
    def get_instrument(instrument_name):
        return BusinessObjectStandin()

    @hookimpl
    def get_instrument_proxy(instrument_name):
        return BusinessObjectStandin()

    @hookimpl
    def get_tester(tester_name):
        if tester_name == "TDKMicronas.MiniSCT":
            return MiniSCT.MiniSCT()

    @hookimpl
    def get_general_purpose_function(func_name):
        print(f"Get General Purpose Function: {func_name}")
        return BusinessObjectStandin()

    @hookimpl
    def get_configuration_options(object_name):
        return []
