# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
from typing import Optional, Tuple

# Qt imports
from qtpy.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout

# Third-party imports
from pygit2 import init_repository, Repository, reference_is_valid_name
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.vcs import VCSInitializationProvider

# Localization
_ = get_translation('spyder')


class GitHubInitialization(VCSInitializationProvider):
    """Widget used to clone/create a git repository hosted in GitHub."""

    NAME = 'github'
    RANK = 0

