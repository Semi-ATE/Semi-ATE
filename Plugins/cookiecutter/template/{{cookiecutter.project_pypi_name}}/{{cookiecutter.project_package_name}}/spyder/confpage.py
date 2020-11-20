# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © {% now 'local', '%Y' %}, {{ cookiecutter.full_name }}
#
# Licensed under the terms of the {{ cookiecutter.open_source_license }}
# ----------------------------------------------------------------------------
"""
{{cookiecutter.project_name}} Preferences Page.
"""
from spyder.api.preferences import PluginConfigPage
from spyder.api.translations import get_translation

_ = get_translation("{{cookiecutter.project_package_name}}.spyder")


class {{cookiecutter.project_name.replace(" ", "")}}ConfPage(PluginConfigPage):

    # --- PluginConfigPage API
    # ------------------------------------------------------------------------
    def setup_page(self):
        pass
