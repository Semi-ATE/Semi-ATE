# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
from typing import Optional, List, Union, Dict, Tuple, Any

# Qt imports
from qtpy.QtCore import Qt, QAbstractListModel, Signal, QObject, QModelIndex
from qtpy.QtWidgets import (QWidget, QLabel, QLineEdit, QHBoxLayout, QComboBox,
                            QVBoxLayout)

# Third-party imports
import requests
from pygit2 import init_repository, Repository, reference_is_valid_name
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.vcs import VCSInitializationProvider
from ate_spyder.widgets.vcs.schema import (
    GitHubUser, GitHubOrganization, GitHubOrganizationInfo,
    GitHubRepository, GitHubBranch)

# Localization
_ = get_translation('spyder')

# GitHub API URL
GITHUB_API_URL = 'https://api.github.com'
BASE_HEADERS = {
    "Accept": "application/vnd.github+json"
}

def perform_http_call(url: str, headers: Dict) -> Tuple[Any, Optional[str]]:
    try:
        req = requests.get(url, headers=headers)
    except requests.ConnectionError as e:
        msg = e.strerror
        return None, msg

    try:
        req.raise_for_status()
    except requests.HTTPError as e:
        return None, e.strerror

    return req.json(), None


class GitHubOrgModel(QAbstractListModel):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.organizations: List[GitHubOrganization] = []

    def set_organizations(self, user: GitHubUser, headers: Dict) -> bool:
        org_url =  f'{GITHUB_API_URL}/user/orgs'
        body: List[GitHubOrganizationInfo]
        body, err_msg = perform_http_call(org_url, headers)

        if err_msg is not None:
            self.sig_err_occurred.emit(err_msg)
            return False

        all_orgs: List[GitHubOrganization] = []
        for org_info in body:
            org_url = org_info['url']
            org: GitHubOrganization
            org, err_msg = perform_http_call(org_url, headers)
            if err_msg is not None:
                self.sig_err_occurred.emit(err_msg)
                return False

            org_allows_creation = org['members_can_create_repositories']
            if org_allows_creation:
                all_orgs.append(org)

        user_org = {
            'login': user['login'],
            'repos_url': f'{GITHUB_API_URL}/user/repos'
                         '?affiliation=owner,collaborator&sort=pushed'
        }
        all_orgs = [user_org] + all_orgs

        self.beginResetModel()
        self.organizations: List[GitHubOrganization] = all_orgs
        self.endResetModel()
        return True

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        org = self.organizations[row]
        if role == Qt.DisplayRole:
            org_login = org['login']
            return org_login

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.organizations)


class GitHubRepoModel(QAbstractListModel):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.repositories: List[GitHubRepository] = []

    def set_repositories(self, org: GitHubOrganization, headers: Dict) -> bool:
        repos_url = org['repos_url']
        body: List[GitHubRepository]
        body, err_msg = perform_http_call(repos_url, headers)

        if err_msg is not None:
            self.sig_err_occurred.emit(err_msg)
            return False

        repositories: List[GitHubRepository] = []
        for repo in body:
            is_archived = repo['archived']
            allow_forking = repo['allow_forking']
            permissions = repo['permissions']
            if is_archived:
                continue

            if not permissions['push'] and not allow_forking:
                continue

            repositories.append(repo)

        self.repositories = repositories
        return True

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        repo = self.repositories[row]
        if role == Qt.DisplayRole:
           repo_name = repo['full_name']
           return repo_name

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.repositories)


class GitHubBranchModel(QAbstractListModel):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.branches: List[GitHubBranch] = []

    def set_branches(self, repo: GitHubRepository, headers: Dict) -> bool:
        branches_url = repo['branches_url']
        body: List[GitHubBranch]



    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        branch = self.branches[row]
        if role == Qt.DisplayRole:
            branch_name = branch['name']
            return branch_name

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.branches)


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

