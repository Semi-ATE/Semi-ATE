
from ate_common.logger import Logger
import pluggy
hookspec = pluggy.HookspecMarker("ate.org")
hookimpl = pluggy.HookimplMarker("ate.org")


class ATEPlugin:

    @hookspec
    def get_plugin_identification():
        pass

    @hookspec
    def get_importer_names():
        pass

    @hookspec
    def get_exporter_names():
        pass

    @hookspec
    def get_equipment_names():
        pass

    @hookspec
    def get_devicepin_importer_names():
        pass

    @hookspec
    def get_instrument_names():
        pass

    @hookspec
    def get_general_purpose_function_names():
        pass

    @hookspec
    def get_tester_names():
        pass

    @hookimpl
    def get_tester_master_names():
        pass

    @hookspec
    def get_importer(importer_name):
        pass

    @hookspec
    def get_exporter(exporter_name):
        pass

    @hookspec
    def get_equipment(equipment_name):
        pass

    @hookspec
    def get_devicepin_importer(importer_name):
        pass

    @hookspec
    def get_instrument(instrument_name, logger: Logger):
        pass

    @hookspec
    def get_tester(tester_name):
        pass

    @hookspec
    def get_general_purpose_function(func_name, logger: Logger):
        pass

    @hookspec
    def get_configuration_options(object_name):
        pass
