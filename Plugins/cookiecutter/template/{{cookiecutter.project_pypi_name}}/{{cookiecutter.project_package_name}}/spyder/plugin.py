# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © {% now 'local', '%Y' %}, {{ cookiecutter.full_name }}
#
# Licensed under the terms of the {{ cookiecutter.open_source_license }}
# ----------------------------------------------------------------------------
"""
{{cookiecutter.project_name}} Plugin.
"""

from qtpy.QtGui import QIcon
from spyder.api.plugins import Plugins
from spyder.api.plugins import {% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' %}SpyderDockablePlugin{% else %}SpyderPluginV2{% endif %}
from spyder.api.translations import get_translation

from {{cookiecutter.project_package_name}}.spyder.confpage import {{cookiecutter.project_name.replace(" ", "")}}ConfPage
{% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' %}from {{cookiecutter.project_package_name}}.spyder.widgets import {{cookiecutter.project_name.replace(" ", "")}}Widget{% else %}from {{cookiecutter.project_package_name}}.spyder.container import {{cookiecutter.project_name.replace(" ", "")}}Container{% endif %}

_ = get_translation("{{cookiecutter.project_package_name}}.spyder")


class {{cookiecutter.project_name.replace(" ", "")}}({% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' %}SpyderDockablePlugin{% else %}SpyderPluginV2{% endif %}):
    """
    {{cookiecutter.project_name}} plugin.
    """

    NAME = "{{cookiecutter.project_package_name}}"
    REQUIRES = []
    OPTIONAL = []
    {% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' -%}
    WIDGET_CLASS = {{cookiecutter.project_name.replace(" ", "")}}Widget
    {% else -%}
    CONTAINER_CLASS = {{cookiecutter.project_name.replace(" ", "")}}Container
    {% endif -%}
    CONF_SECTION = NAME
    CONF_WIDGET_CLASS = {{cookiecutter.project_name.replace(" ", "")}}ConfPage

    # --- Signals

    # --- SpyderPluginV2 API
    # ------------------------------------------------------------------------
    def get_name(self):
        return _("{{cookiecutter.project_name}}")

    def get_description(self):
        return _("{{cookiecutter.project_short_description}}")

    def get_icon(self):
        return QIcon()

    def register(self):
        {% if cookiecutter.plugin_type == 'Spyder Dockable Plugin' -%}widget = self.get_widget(){% else %}container = self.get_container(){% endif %}

    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True

    # --- Public API
    # ------------------------------------------------------------------------
