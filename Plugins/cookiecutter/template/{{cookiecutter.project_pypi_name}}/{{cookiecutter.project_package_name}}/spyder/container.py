# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © {% now 'local', '%Y' %}, {{ cookiecutter.full_name }}
#
# Licensed under the terms of the {{ cookiecutter.open_source_license }}
# ----------------------------------------------------------------------------
"""
{{cookiecutter.project_name}} Main Container.
"""
from spyder.api.translations import get_translation
from spyder.api.widgets import PluginMainContainer

_ = get_translation("{{cookiecutter.project_package_name}}.spyder")


class {{cookiecutter.project_name.replace(" ", "")}}Container(PluginMainContainer):
    DEFAULT_OPTIONS = {
    }

    # Signals

    def __init__(self, name, plugin, parent=None, options=DEFAULT_OPTIONS):
        super().__init__(name, plugin, parent=parent, options=options)

    # --- PluginMainContainer API
    # ------------------------------------------------------------------------
    def setup(self):
        pass

    def on_option_update(self, option, value):
        pass

    def update_actions(self):
        pass

    # --- Public API
    # ------------------------------------------------------------------------
