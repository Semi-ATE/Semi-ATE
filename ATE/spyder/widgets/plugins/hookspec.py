
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
    def get_actuator_names():
        pass

    @hookspec
    def get_instrument_names():
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
    def get_actuator(required_capability):
        pass

    @hookimpl
    def get_actuator_proxy(required_capability):
        pass

    @hookspec
    def get_instrument(instrument_name):
        pass
