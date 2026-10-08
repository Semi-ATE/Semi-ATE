# -*- coding: utf-8 -*-
"""
Configuration file for Pytest
"""
import os

# NOTE: Muss vor allen anderen Imports stehen!
os.environ['SPYDER_PYTEST'] = 'True'
os.environ.setdefault('QT_API', 'pyqt5')   # Binding für qtpy festlegen

import pytest


@pytest.fixture
def qt_app(qapp):
    """Alias auf das qapp-Fixture von pytest-qt (für ältere Tests)."""
    return qapp