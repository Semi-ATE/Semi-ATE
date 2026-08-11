# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
Configuration file for Pytest
"""

import os
import pytest
from qtpy.QtWidgets import QApplication
import sys

# To activate/deactivate certain things for pytest's only
# NOTE: Please leave this before any other import here!!
os.environ['SPYDER_PYTEST'] = 'True'


@pytest.fixture(scope="session")
def qapp():
    """QApplication für alle Qt-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def qt_app(qapp):
    """Stelle sicher, dass QApplication vorhanden ist"""
    return qapp