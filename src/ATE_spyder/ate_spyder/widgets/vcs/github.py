# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
from typing import Optional, List

# Qt imports
from qtpy.QtCore import QAbstractListModel, Signal, QObject
from qtpy.QtWidgets import (QWidget, QLabel, QLineEdit, QHBoxLayout, QComboBox,
                            QVBoxLayout)

# Third-party imports
import requests
from pygit2 import init_repository, Repository, reference_is_valid_name
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.vcs import VCSInitializationProvider
from ate_spyder.widgets.vcs.schema import (
    GitHubUser, GitHubOrganization, GitHubRepository, GitHubBranch)

# Localization
_ = get_translation('spyder')

# GitHub API URL
GITHUB_API_URL = 'https://api.github.com'


class GitHubOrgModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.organizations: List[GitHubOrganization] = []


class GitHubRepoModel(QAbstractListModel):
    pass


class GitHubBranchModel(QAbstractListModel):
    pass


class GitHubInitialization(VCSInitializationProvider):
    """Widget used to clone/create a git repository hosted in GitHub."""

    NAME = 'github'
    RANK = 0

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Personal access token
        pat_label = QLabel(_('Personal access token'))
        self.pat_text = QLineEdit()
        self.pat_text.textChanged.connect(self.pat_changed)

        pat_layout = QHBoxLayout()
        pat_layout.addWidget(pat_label)
        pat_layout.addWidget(self.pat_text)

        # Organization combobox
        org_label = QLabel(_('Organization'))
        self.org_combobox = QComboBox()

        org_layout = QHBoxLayout()
        org_layout.addWidget(org_label)
        org_layout.addWidget(self.org_combobox)

        # Repository combobox
        repo_label = QLabel(_('Repository'))
        self.repo_combobox = QComboBox()

        repo_layout = QHBoxLayout()
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_combobox)

        # Branch combobox
        branch_label = QLabel(_('Checkout branch'))
        self.branch_combo = QComboBox()

        branch_layout = QHBoxLayout()
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_combo)

        # Widget layout
        layout = QVBoxLayout()
        layout.addLayout(pat_layout)
        layout.addLayout(org_layout)
        layout.addLayout(repo_layout)
        layout.addLayout(branch_layout)

        # Models and connections
        self.github_org_model = GitHubOrgModel(self)
        self.github_repo_model = GitHubRepoModel(self)
        self.github_branch_model = GitHubBranchModel(self)

        self.current_user: Optional[GitHubUser] = None
