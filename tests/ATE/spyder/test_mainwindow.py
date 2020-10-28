# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for the main window.
"""

# Third party imports
# import pytest
# from spyder.app import start
# from spyder.app.mainwindow import MainWindow
# from spyder.config.manager import CONF

# # Local imports
# from ATE.spyder.plugin import ATEPluginProject, ATEProject


# # --- Fixtures
# # ----------------------------------------------------------------------------
# @pytest.fixture
# def main_window(qtbot):
#     """Main Window fixture."""
#     CONF.reset_to_defaults()
#     window = start.main()
#     main_window.window = window
#     qtbot.addWidget(window)
#     yield window


# def test_projects(main_window, qtbot):
#     types = main_window.projects.get_project_types()
#     assert ATEPluginProject.ID in types
#     assert ATEProject.ID in types
#     main_window.close()
