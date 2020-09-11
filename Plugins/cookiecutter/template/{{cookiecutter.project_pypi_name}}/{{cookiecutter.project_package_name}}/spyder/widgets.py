# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © {% now 'local', '%Y' %}, {{ cookiecutter.full_name }}
#
# Licensed under the terms of the {{ cookiecutter.open_source_license }}
# ----------------------------------------------------------------------------
"""
{{cookiecutter.project_name}} Main Widget.
"""
from spyder.api.translations import get_translation
{% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' %}from spyder.api.widgets import PluginMainWidget{% else %}from spyder.api.widgets.mixins import SpyderWidgetMixin{% endif %}

_ = get_translation('{{cookiecutter.project_package_name}}.spyder')

{% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' %}
class {{cookiecutter.project_name.replace(" ", "")}}Widget(PluginMainWidget):
    DEFAULT_OPTIONS = {
    }

    # Signals

    def __init__(self, name, plugin, parent=None, options=DEFAULT_OPTIONS):
        super().__init__(name, plugin, parent=parent, options=options)

    # --- PluginMainContainer API
    # ------------------------------------------------------------------------
    def get_title(self):
        return _("{{cookiecutter.project_name}}")

    def get_focus_widget(self):
        pass

    def setup(self):
        pass

    def on_option_update(self, option, value):
        pass

    def update_actions(self):
        pass

    # --- Public API
    # ------------------------------------------------------------------------
{% endif -%}
