# -*- coding: utf-8 -*-
"""
plugin_semictrl.

Created on Thu Jan  7 17:18:03 2021

@author: ZLin526F


"""
from ate_semiateplugins.hookspec import hookimpl
from labml_adjutancy.ctrl.labctrl import LabCtrl

__author__ = "Zlin526F"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.6"


mqttc = None


class Plugin:
    @staticmethod
    def prefix():
        return "SemiCtrl"

    @hookimpl
    def get_plugin_identification():
        return {"Name": f"{Plugin.prefix()} Plugin", "Version": __version__}

    @hookimpl
    def get_importer_names():
        return [
            {
                "display_name": f"{Plugin.prefix()} Importer",
                "version": __version__,
                "name": f"{Plugin.prefix()}.Importer",
            }
        ]

    @hookimpl
    def get_exporter_names():
        return [
            {
                "display_name": f"{Plugin.prefix()} Exporter",
                "version": __version__,
                "name": f"{Plugin.prefix()}.Exporter",
            }
        ]

    @hookimpl
    def get_equipment_names():
        return [
            {
                "display_name": f"{Plugin.prefix()} Equipment",
                "version": __version__,
                "name": f"{Plugin.prefix()}.Equipment",
            }
        ]

    @hookimpl
    def get_devicepin_importer_names():
        return [
            {
                "display_name": f"{Plugin.prefix()} Pinimport",
                "version": __version__,
                "name": f"{Plugin.prefix()}.Pinimport",
            }
        ]

    @hookimpl
    def get_instrument_names():
        return [
            {
                "display_name": "Semi-Control V" + __version__,
                "version": __version__,
                "manufacturer": "TDK Micronas Labor",
                "name": f"{Plugin.prefix()}.Control",
            }
        ]  # this is the instrument_name in get_instrument()

    @hookimpl
    def get_general_purpose_function_names():
        return []

    @hookimpl
    def get_importer(importer_name):
        if Plugin.prefix() in importer_name:
            print(f"{Plugin.prefix()}.get_importer")
            return LabCtrl()

    @hookimpl
    def get_exporter(exporter_name):
        if Plugin.prefix() in exporter_name:
            print(f"{Plugin.prefix()}.get_exporter")
            return LabCtrl()

    @hookimpl
    def get_equipment(equipment_name):
        if "SemiCtrl." in equipment_name:
            print(f"{Plugin.prefix()}.get_equipment")
            return LabCtrl()

    @hookimpl
    def get_devicepin_importer(importer_name):
        if "SemiCtrl." in importer_name:
            print(f"{Plugin.prefix()}.get_devicepin_importer")
            return LabCtrl()

    @hookimpl
    def get_instrument(instrument_name: str, logger):
        if instrument_name == "SemiCtrl.Control":
            print(f"{Plugin.prefix()}.get_instrument")
            return LabCtrl(logger)

    @hookimpl
    def get_instrument_proxy(instrument_name):
        if Plugin.prefix() in instrument_name:
            print(f"{Plugin.prefix()}.get_instrument_proxy")
            return LabCtrl()

    @hookimpl
    def get_configuration_options(object_name):
        if Plugin.prefix() in object_name:
            print(f"{Plugin.prefix()}.get_configuration_options")
            return LabCtrl.parameter[object_name]
