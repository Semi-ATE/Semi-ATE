# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
from functools import wraps, partial
from threading import Semaphore, Lock, RLock
from typing import Optional, List, Union, Dict, Tuple, Any, Callable

# Qt imports
from qtpy.QtCore import (Qt, QAbstractListModel, Signal, QObject, QModelIndex,
                         QThread)
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


class AtomicCounter:
    def __init__(self, initial_value: int):
        self.lock = Lock()
        self.zero_lock = RLock()
        self.count = initial_value
        self.initial_value = initial_value

    def __iadd__(self, other: int):
        with self.lock:
            if self.count == self.initial_value:
                self.zero_lock.acquire()

            self.count += other

            if self.count == self.initial_value:
                self.zero_lock.release()

    def __isub__(self, other: int):
        with self.lock:
            self.count -= other

            if self.count == self.initial_value:
                self.zero_lock.release()

    def __ge__(self, other: int):
        with self.lock:
            return self.count > other


class HTTPThreadRequestThread(QThread):
    sig_thread_response = Signal(object, str)

    def __init__(self, parent: Optional[QObject] = None,
                 url: Optional[str] = None,
                 headers: Optional[Dict] = None) -> None:
        super().__init__(parent)
        self.url = url
        self.headers = headers

    def run(self) -> None:
        print('**************************', self.url)
        body, err_msg = perform_http_call(self.url, self.headers)
        self.sig_thread_response.emit(body, err_msg)


class HTTPRequestPerformer:
    MAX_CONCURRENT_REQUESTS = 5

    def __init__(self) -> None:
        self.http_semaphore = Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.http_threads = set({})

    def perform_http_call(self, url: str, headers: Dict,
                          callback: Callable[[Any, Optional[str]], Any]):
        @wraps(callback)
        def wrapped_callback(body: Any, err_msg: Optional[str],
                             thread: Optional[HTTPThreadRequestThread] = None):
            print(callback)
            self.http_semaphore.release(1)
            self.http_threads -= {thread}
            callback(body, err_msg)

        self.http_semaphore.acquire()
        thread = HTTPThreadRequestThread(self, url, headers)
        thread.sig_thread_response.connect(
            partial(wrapped_callback, thread=thread))
        thread.start()
        self.http_threads |= {thread}


class GitHubOrgRetrieverThread(QThread, HTTPRequestPerformer):
    sig_orgs_retrieved = Signal(list)

    def __init__(self, parent: Optional[QObject],
                 org_info: List[GitHubOrganizationInfo],
                 headers: Optional[dict] = None):
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)

        self.org_info = org_info
        self.all_orgs: List[GitHubOrganization] = []
        self.headers = headers
        self.counter: Optional[AtomicCounter] = None

    def append_org_result(self, org: GitHubOrganization, err_msg: str):
        self.counter -= 1
        if err_msg == '':
            return

        org_allows_creation = org['members_can_create_repositories']
        if org_allows_creation:
            self.all_orgs.append(org)

    def run(self) -> None:
        self.counter = AtomicCounter(0)
        for org_info in self.org_info:
            org_url = org_info['url']
            org: GitHubOrganization
            self.counter += 1
            self.perform_http_call(
                org_url, self.headers, self.append_org_result)

        self.sig_orgs_retrieved.emit(self.all_orgs)


class GitHubOrgModel(QAbstractListModel, HTTPRequestPerformer):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)
        self.organizations: List[GitHubOrganization] = []

    def set_organizations(self, user: GitHubUser, headers: Dict) -> bool:
        org_url =  f'{GITHUB_API_URL}/user/orgs'
        body: List[GitHubOrganizationInfo]
        self.organizations: List[GitHubOrganization] = []
        self.org_thread: Optional[GitHubOrgRetrieverThread] = None

        user_org = {
            'login': user['login'],
            'repos_url': f'{GITHUB_API_URL}/user/repos'
                         '?affiliation=owner,collaborator&sort=pushed'
        }
        self.organizations.append(user_org)

        self.perform_http_call(org_url, headers,
                               partial(self.organizations_callback,
                                       headers=headers))

    def organizations_callback(self, body: List[GitHubOrganizationInfo],
                               err_msg: Optional[str],
                               headers: Optional[Dict] = None):
        if err_msg != '':
            self.sig_err_occurred.emit(err_msg)
            return False

        print('----------------------------------')

        def set_orgs(orgs: List[GitHubOrganization]):
            self.beginResetModel()
            self.organizations += orgs
            self.org_thread = None
            self.endResetModel()

        self.org_thread = GitHubOrgRetrieverThread(self, body, headers)
        self.org_thread.sig_orgs_retrieved.connect(set_orgs)
        self.org_thread.start()
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
        body, err_msg = perform_http_call(branches_url, headers)

        if err_msg is not None:
            self.sig_err_occurred.emit(err_msg)
            return False

        self.branches = body

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
        self.branch_combobox = QComboBox()

        branch_layout = QHBoxLayout()
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_combobox)

        # Widget layout
        layout = QVBoxLayout()
        layout.addLayout(pat_layout)
        layout.addLayout(org_layout)
        layout.addLayout(repo_layout)
        layout.addLayout(branch_layout)
        self.setLayout(layout)

        # Models and connections
        self.headers = {}
        self.current_user: Optional[GitHubUser] = None
        self.github_org_model = GitHubOrgModel(self)
        self.github_repo_model = GitHubRepoModel(self)
        self.github_branch_model = GitHubBranchModel(self)

        self.github_org_model.sig_err_occurred.connect(
            lambda msg: self.sig_update_status.emit(False, msg))
        self.github_repo_model.sig_err_occurred.connect(
            lambda msg: self.sig_update_status.emit(False, msg))
        self.github_branch_model.sig_err_occurred.connect(
            lambda msg: self.sig_update_status.emit(False, msg))

        self.org_combobox.setModel(self.github_org_model)
        self.repo_combobox.setModel(self.github_repo_model)
        self.branch_combobox.setModel(self.github_branch_model)

        self.pat_text.textChanged.connect(self.pat_changed)
        self.org_combobox.currentIndexChanged.connect(self.org_selected)
        self.repo_combobox.currentIndexChanged.connect(self.repo_selected)
        self.branch_combobox.currentIndexChanged.connect(self.branch_selected)

        self.pat_text.setText('')
        self.org_combobox.setEnabled(False)
        self.repo_combobox.setEnabled(False)
        self.branch_combobox.setEnabled(False)

    @classmethod
    def get_name(cls) -> str:
        return _('GitHub')

    def pat_changed(self, text: str):
        if len(text) < 40:
            msg = _('Personal access token length should contain at '
                    'least 40 characters')
            self.sig_update_status.emit(False, msg)
            return

        self.headers = {
            'Accept': 'application/vnd.github+json',
            "Authorization": f"Bearer {text}"
        }

        # Retrieve GitHub profile for the given token
        body: GitHubUser
        self.sig_update_status.emit(False, _('Retrieving information'))
        body, err_msg = perform_http_call(
            f'{GITHUB_API_URL}/user', self.headers)

        if err_msg is not None:
            self.sig_update_status.emit(False, err_msg)

        self.current_user = body
        self.github_org_model.set_organizations(
            self.current_user, self.headers)
        self.org_combobox.setEnabled(True)
        # self.repo_combobox.setEnabled(status)
        # self.branch_combobox.setEnabled(False)


    def org_selected(self, index: int):
        print('---------------------------', index)

    def repo_selected(self, index: int):
        pass

    def branch_selected(self, index: int):
        pass

    def validate(self) -> Tuple[bool, Optional[str]]:
        return False, ''
