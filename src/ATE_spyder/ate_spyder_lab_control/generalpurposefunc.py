"""
Plugin for the LABML general purpose function.

"""
import os
import sys
from pathlib import Path
import importlib
import inspect
from ate_common.logger import LogLevel
from ate_semiateplugins.hookspec import hookimpl
from labml_adjutancy.misc import environment
from labml_adjutancy.misc import projectsetup
from labml_adjutancy.register import registermaster

__author__ = "Zlin526F"
__copyright__ = "Copyright 2021, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = '0.0.1'


class Plugin:

    @hookimpl
    def get_plugin_identification():
        return {
            "Name": "LABML Reference Plugin",
            "Version": __version__
        }

    @hookimpl
    def get_importer_names():
        return [
            {"display_name": "Dummy Importer",
             "version": "0.0",
             "name": "LABML.DummyImporter"}]

    @hookimpl
    def get_exporter_names():
        return [
            {"display_name": "Dummy Exporter",
             "version": "0.0",
             "name": "LABML.DummyExporter"}]

    @hookimpl
    def get_equipment_names():
        return [
            {"display_name": "Dummy Equipment",
             "version": "0.0",
             "name": "LABML.DummyEquipment"}]

    @hookimpl
    def get_devicepin_importer_names():
        return [
            {"display_name": "Dummy Pinimport",
             "version": "0.0",
             "name": "LABML.DummyPinimport"}]

    @hookimpl
    def get_instrument_names():
        return []

    @hookimpl
    def get_general_purpose_function_names():
        return [
            {"display_name": "Project Setup",
             "version": projectsetup.__version__,
             "manufacturer": "TDK Micronas Labor",
             "name": "LABML.Setup"},
            {"display_name": "Registermaster",
             "version": registermaster.__version__,
             "manufacturer": "TDK Micronas Labor",
             "name": "LABML.Registermaster"}
            ]

    @hookimpl
    def get_importer(importer_name):
        return

    @hookimpl
    def get_exporter(exporter_name):
        return

    @hookimpl
    def get_equipment(equipment_name):
        return

    @hookimpl
    def get_devicepin_importer(importer_name):
        return

    @hookimpl
    def get_instrument(instrument_name: str, logger):
        pass

    @hookimpl
    def get_instrument_proxy(instrument_name):
        pass

    @hookimpl
    def get_general_purpose_function(func_name: str, logger):
        if func_name == "LABML.Setup":
            return projectsetup.ProjectSetup(logger)
        elif func_name == "LABML.Registermaster":
            return registermaster.RegisterMaster(logger)

    @hookimpl
    def get_configuration_options(object_name):
        if object_name == "LABML.Setup":
            return ["Network prefix", "working directory", "add path", 'instance name', 'filename']
        elif object_name == "LABML.Registermaster":
            return ['instance name', 'filename', 'read mod write', 'reset value']
