# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
import os
import os.path as osp
import time
import shutil
from functools import partial
from queue import Queue
from threading import Semaphore
from typing import Optional, List, Dict, Tuple, Any, Callable, Union

# Qt imports
from qtpy.QtCore import (Qt, QAbstractListModel, Signal, QObject, QModelIndex,
                         QThread)
from qtpy.QtWidgets import (QWidget, QLabel, QLineEdit, QHBoxLayout, QComboBox,
                            QVBoxLayout, QDialog, QCheckBox, QGroupBox,
                            QDialogButtonBox)

# Third-party imports
import requests
from pygit2 import clone_repository, RemoteCallbacks, UserPass
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.vcs import VCSInitializationProvider
from ate_spyder.widgets.vcs.schema import (
    GitHubUser, GitHubOrganization, GitHubOrganizationInfo,
    GitHubRepository, GitHubBranch, GitHubLicenses)

# Spyder imports
from spyder.widgets.simplecodeeditor import SimpleCodeEditor

# Localization
_ = get_translation('spyder')

# GitHub API URL
GITHUB_API_URL = 'https://api.github.com'
BASE_HEADERS = {
    "Accept": "application/vnd.github+json"
}

ReqResultError = Tuple[Any, Optional[str]]
ReqResultStatusErr = Tuple[Any, Optional[str], int]


def perform_http_call(
        url: str, headers: Dict,
        return_status_code: bool = False,
        verb: str = 'GET',
        body: Optional[dict] = None) -> Union[
            ReqResultError, ReqResultStatusErr]:
    try:
        req = requests.request(verb, url, headers=headers, json=body)
    except requests.ConnectionError as e:
        msg = e.strerror
        ret = None, msg
        if return_status_code:
            ret += (-1,)
        return ret
    except requests.exceptions.InvalidHeader:
        ret = None, _('Invalid token format')
        if return_status_code:
            ret += (400,)
        return ret

    try:
        req.raise_for_status()
    except requests.HTTPError as e:
        ret = None, e.strerror
        if return_status_code:
            ret += (req.status_code,)
        return ret

    ret = req.json(), None
    if return_status_code:
        ret += (req.status_code,)
    return ret


class HTTPThreadRequestThread(QThread):
    sig_thread_response = Signal(object, str)

    def __init__(self, parent: Optional[QObject] = None,
                 url: Optional[str] = None,
                 headers: Optional[Dict] = None,
                 queue: Optional[Queue] = None,
                 return_status_code: bool = False,
                 verb: str = 'GET',
                 body: Optional[dict] = None) -> None:
        super().__init__(parent)
        self.url = url
        self.headers = headers
        self.queue = queue
        self.return_status_code = return_status_code
        self.verb = verb
        self.body = body

    def run(self) -> None:
        print('**************************', self.verb, self.url)
        ret = perform_http_call(
            self.url, self.headers, self.return_status_code,
            self.verb, self.body)
        self.queue.put(ret)


class HTTPRequestPerformer:
    MAX_CONCURRENT_REQUESTS = 5

    def __init__(self) -> None:
        self.http_semaphore = Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.http_threads = set({})

    def perform_http_call(self, url: str, headers: Dict,
                          callback: Callable[[Any, Optional[str]], Any],
                          queue: Optional[Queue] = None,
                          return_status_code: bool = False,
                          verb: str = 'GET',
                          body: Optional[dict] = None):
        with self.http_semaphore:
            use_queue = queue or Queue()
            thread = HTTPThreadRequestThread(
                None, url, headers, use_queue, return_status_code, verb, body)
            thread.start()
            self.http_threads |= {thread}

            if queue is None:
                print(f'Awaiting response for {url}')
                ret = use_queue.get()
                print(f'Got response for {url}')

        if queue is None:
            print(f'Calling {callback}')
            callback(*ret)


class GitHubOrgRetrieverThread(QThread, HTTPRequestPerformer):
    sig_orgs_retrieved = Signal(list)
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject],
                 org_info: List[GitHubOrganizationInfo],
                 headers: Optional[dict] = None):
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)

        self.org_info = org_info
        self.headers = headers

    def append_org_result(self, org: GitHubOrganization, err_msg: str):
        self.counter -= 1
        if err_msg == '':
            return

        org_allows_creation = org['members_can_create_repositories']
        if org_allows_creation:
            self.all_orgs.append(org)

    def run(self) -> None:
        queue = Queue()
        for org_info in self.org_info:
            org_url = org_info['url']
            self.perform_http_call(
                org_url, self.headers, self.append_org_result, queue)

        # Wait for tasks to be enqueued
        counter = len(self.org_info)
        all_orgs: List[GitHubOrganization] = []

        while counter > 0:
            org: GitHubOrganization
            org, err_msg = queue.get()
            counter -= 1

            if err_msg is not None:
                self.sig_err_occurred.emit(err_msg)
            else:
                org_allows_creation = org['members_can_create_repositories']
                if org_allows_creation:
                    all_orgs.append(org)

        self.sig_err_occurred.emit(
            f'A total of {len(all_orgs)} organizations were found')
        self.sig_orgs_retrieved.emit(all_orgs)


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
                         '?affiliation=owner,collaborator&sort=pushed',
            'members_can_create_private_repositories': True
        }
        self.organizations.append(user_org)

        self.perform_http_call(org_url, headers,
                               partial(self.organizations_callback,
                                       headers=headers))

    def organizations_callback(self, body: List[GitHubOrganizationInfo],
                               err_msg: Optional[str],
                               headers: Optional[Dict] = None):
        # print(body, err_msg,)
        if err_msg is not None:
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
        self.org_thread.sig_err_occurred.connect(self.sig_err_occurred)
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

    def clear(self):
        self.beginResetModel()
        self.organizations = []
        self.org_thread = None
        self.endResetModel()

    def __getitem__(self, index: int) -> GitHubOrganization:
        return self.organizations[index]


class GitHubRepoModel(QAbstractListModel, HTTPRequestPerformer):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)
        self.repositories: List[GitHubRepository] = []

    def set_repositories(self, org: GitHubOrganization, headers: Dict) -> bool:
        repos_url = org['repos_url']
        self.perform_http_call(
            repos_url, headers, self.process_repositories)

    def process_repositories(self, repos: List[GitHubRepository],
                             err_msg: Optional[str]):
        if err_msg is not None:
            self.sig_err_occurred.emit(err_msg)
            return

        repositories: List[GitHubRepository] = []
        for repo in repos:
            is_archived = repo['archived']
            allow_forking = repo['allow_forking']
            permissions = repo['permissions']
            if is_archived:
                continue

            if not permissions['push'] and not allow_forking:
                continue

            repositories.append(repo)

        self.beginResetModel()
        self.repositories = repositories
        self.endResetModel()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        if role == Qt.DisplayRole:
           if row == 0:
                return _('Create new repository...')

           repo = self.repositories[row - 1]
           repo_name = repo['full_name']
           return repo_name

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.repositories) + 1

    def clear(self):
        self.beginResetModel()
        self.repositories = []
        self.endResetModel()

    def prepend_repository(self, repo: GitHubRepository):
        self.beginResetModel()
        self.repositories = [repo] + self.repositories
        self.endResetModel()

    def __getitem__(self, index: int) -> GitHubRepository:
        return self.repositories[index]

    def __len__(self) -> int:
        return len(self.repositories)


class GitHubBranchModel(QAbstractListModel, HTTPRequestPerformer):
    sig_err_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)
        self.branches: List[GitHubBranch] = []

    def set_branches(self, repo: GitHubRepository, headers: Dict) -> bool:
        branches_url = repo['branches_url'].replace('{/branch}', '')
        body: List[GitHubBranch]

        def handle_branches(branches: List[GitHubBranch],
                            err_msg: Optional[str]):
            if err_msg is not None:
                self.sig_err_occurred.emit(err_msg)
                return

            self.beginResetModel()
            self.branches = branches
            self.endResetModel()

        self.perform_http_call(branches_url, headers, handle_branches)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        branch = self.branches[row]
        if role == Qt.DisplayRole:
            branch_name = branch['name']
            return branch_name

    def clear(self):
        self.beginResetModel()
        self.branches = []
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.branches)

    def __getitem__(self, idx: int) -> GitHubBranch:
        return self.branches[idx]


class GitHubLicenseModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.index_mapping = list(GitHubLicenses.keys())

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        row = index.row()
        if row == 0:
            if role == Qt.DisplayRole:
                return _('No license specified')
            return

        license_name = self.index_mapping[row - 1]
        if role == Qt.DisplayRole:
           return license_name
        elif role == Qt.ToolTipRole:
            license_identifier = GitHubLicenses[license_name]
            return license_identifier

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(GitHubLicenses) + 1

    def __getitem__(self, idx: int) -> Optional[str]:
        if idx == 0:
            return None

        license_name = self.index_mapping[idx - 1]
        license_identifier = GitHubLicenses[license_name]
        return license_identifier


class GitHubNewRepoDialog(QDialog, HTTPRequestPerformer):
    sig_dialog_enabled = Signal(bool)
    sig_dlg_complete = Signal()

    def __init__(self, parent: Optional[QWidget] = None,
                 org: Optional[GitHubOrganization] = None,
                 repo_name: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(parent)
        HTTPRequestPerformer.__init__(self)

        self.org = org
        self.headers = headers
        self.new_repo_info: Optional[GitHubRepository] = None

        self.setWindowTitle(_('New GitHub repository'))

        # Organization name
        org_label = QLabel(_('Organization name'))
        org_name = QLabel(org['login'])

        org_layout = QHBoxLayout()
        org_layout.addWidget(org_label)
        org_layout.addWidget(org_name)

        # Repository name
        repo_name_label = QLabel(_('Repository name'))
        self.repo_name_text = QLineEdit()

        repo_name_layout = QHBoxLayout()
        repo_name_layout.addWidget(repo_name_label)
        repo_name_layout.addWidget(self.repo_name_text)

        # Repository URL
        repo_url_label = QLabel(_('Homepage (optional)'))
        self.repo_url_text = QLineEdit()

        repo_url_layout = QHBoxLayout()
        repo_url_layout.addWidget(repo_url_label)
        repo_url_layout.addWidget(self.repo_url_text)

        # Repository description
        repo_description_group = QGroupBox(_('Description (optional)'))
        self.repo_description_text = SimpleCodeEditor(self)

        repo_description_layout = QHBoxLayout()
        repo_description_layout.addWidget(self.repo_description_text)
        repo_description_group.setLayout(repo_description_layout)

        # Repository visibility
        self.repo_private_check = QCheckBox(_('Private repository'))

        # Initialize README
        self.repo_init_readme_check = QCheckBox(_('Initialize with README'))

        # Repository license template
        repo_license_label = QLabel(_('License (optional)'))
        self.repo_license_combobox = QComboBox()

        repo_license_layout = QHBoxLayout()
        repo_license_layout.addWidget(repo_license_label)
        repo_license_layout.addWidget(self.repo_license_combobox)

        # Feedback label
        self.status_msg = QLabel()

        # Dialog layout
        layout = QVBoxLayout()
        layout.addLayout(org_layout)
        layout.addLayout(repo_name_layout)
        layout.addLayout(repo_url_layout)
        layout.addWidget(repo_description_group)
        layout.addWidget(self.repo_private_check)
        layout.addWidget(self.repo_init_readme_check)
        layout.addLayout(repo_license_layout)
        layout.addWidget(self.status_msg)
        self.setLayout(layout)

        # Setup, models and initialization
        self.add_button_box(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.license_model = GitHubLicenseModel(self)
        self.repo_license_combobox.setModel(self.license_model)

        self.repo_name_text.textChanged.connect(self.check_repo_name)
        self.repo_name_text.setText(repo_name)

        self.repo_description_text.setup_editor(language='md')

        allow_private = org.get(
            'members_can_create_private_repositories', False)
        self.repo_private_check.setChecked(False)
        self.repo_private_check.setVisible(allow_private)

        self.sig_dlg_complete.connect(self.accept)

    def add_button_box(self, stdbtns):
        """Create dialog button box and add it to the dialog layout"""
        self.bbox = QDialogButtonBox(stdbtns)
        self.bbox.accepted.connect(self.create_repository)
        self.bbox.rejected.connect(self.reject)
        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(self.bbox)
        self.layout().addLayout(btnlayout)

        ok_button = self.bbox.button(QDialogButtonBox.Ok)
        self.sig_dialog_enabled.connect(ok_button.setEnabled)

    def check_repo_name(self, repo_name: str):
        if repo_name == '':
            self.status_msg.setText(_('Repository name must be non-empty'))
            self.sig_dialog_enabled.emit(False)
            return

        def gather_repo_existence(body: Optional[GitHubRepository],
                                  err_msg: Optional[str],
                                  status_code: int):
            if status_code == 404:
                self.status_msg.setText(_('Repository name is available'))
                self.sig_dialog_enabled.emit(True)
            elif status_code == 200:
                self.status_msg.setText(
                    _('A repository named %s already exists' % repo_name))
                self.sig_dialog_enabled.emit(False)
            elif err_msg is not None:
                self.status_msg.setText(err_msg)
                self.sig_dialog_enabled.emit(False)
            else:
                self.status_msg.setText(_('An unexpected error has occurred'))
                self.sig_dialog_enabled.emit(False)

        api_url = f'{GITHUB_API_URL}/repos/{self.org["login"]}/{repo_name}'
        self.perform_http_call(
            api_url, self.headers, gather_repo_existence,
            return_status_code=True)

    def create_repository(self) -> None:
        repo_name = self.repo_name_text.text()
        repo_url = self.repo_url_text.text() or None
        repo_description = self.repo_description_text.toPlainText() or None
        repo_is_private = self.repo_private_check.isChecked()
        repo_init_readme = self.repo_init_readme_check.isChecked()
        license_idx = self.repo_license_combobox.currentIndex()
        repo_license_identifier = self.license_model[license_idx]

        body = {
            'name': repo_name,
            'description': repo_description,
            'homepage': repo_url,
            'private': repo_is_private,
            'auto_init': repo_init_readme,
            'license_template': repo_license_identifier
        }

        def handle_repo_creation(body: Optional[GitHubRepository],
                                 err_msg: Optional[str],
                                 status_code: int):
            print('?????????????????????', body)
            if err_msg is not None:
                self.status_msg.setText(err_msg)

            if status_code == 201:
                self.new_repo_info = body
                self.accept()
            else:
                print('***********************', body, status_code)

        print(body)
        post_url = self.org['repos_url'].split('?')[0]
        # post_url = f'{GITHUB_API_URL}/orgs/{self.org["login"]}/repos'
        self.perform_http_call(post_url, self.headers,
                               handle_repo_creation, return_status_code=True,
                               verb='POST', body=body)

    def accept(self) -> None:
        print('.................. Accepting')
        return super().accept()

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

        # Create new repository dialog
        self.create_new_repo_dlg: Optional[GitHubNewRepoDialog] = None

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
        self.branch_combobox.currentIndexChanged.connect(
            lambda _: self.sig_widget_changed.emit())

        self.pat_text.setText('')
        self.org_combobox.setEnabled(False)
        self.repo_combobox.setEnabled(False)
        self.branch_combobox.setEnabled(False)

        self.select_first_defined_repo = True

    @classmethod
    def get_name(cls) -> str:
        return _('GitHub')

    def pat_changed(self, text: str):
        if len(text) < 40:
            msg = _('Personal access token length should contain at '
                    'least 40 characters')
            self.sig_update_status.emit(False, msg)

            self.github_org_model.clear()
            self.github_repo_model.clear()
            self.github_branch_model.clear()

            self.org_combobox.setEnabled(False)
            self.repo_combobox.setEnabled(False)
            self.branch_combobox.setEnabled(False)
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
        self.repo_combobox.setEnabled(False)
        self.branch_combobox.setEnabled(False)

    def org_selected(self, index: int):
        print('---------------------------', index)
        if not self.org_combobox.isEnabled():
            return
        org = self.github_org_model[index]
        self.repo_combobox.setEnabled(True)
        self.github_repo_model.set_repositories(org, self.headers)
        self.select_first_defined_repo = True

    def repo_selected(self, index: int):
        if index < 0:
            return

        print('////////////////////', index, self.select_first_defined_repo)
        if not self.repo_combobox.isEnabled():
            return

        if index == 0:
            if self.select_first_defined_repo:
                self.select_first_defined_repo = False
                if len(self.github_repo_model) > 0:
                    self.repo_combobox.setCurrentIndex(1)
                return
            self.github_branch_model.clear()
            self.branch_combobox.setEnabled(False)
            # Create new repository
            org = self.github_org_model[self.org_combobox.currentIndex()]
            self.create_new_repo_dlg = GitHubNewRepoDialog(
                self, org, self.ate_project_name, self.headers)
            self.create_new_repo_dlg.finished.connect(
                self.new_repository_created)
            self.create_new_repo_dlg.open()
        else:
            self.select_first_defined_repo = False
            repo = self.github_repo_model[index - 1]
            self.branch_combobox.setEnabled(True)
            self.github_branch_model.set_branches(repo, self.headers)

    def new_repository_created(self, status: int):
        if status == QDialog.Accepted:
            new_repo = self.create_new_repo_dlg.new_repo_info
            if new_repo:
                # self.repo_combobox.setCurrentIndex(-1)
                self.select_first_defined_repo = True
                self.github_repo_model.prepend_repository(new_repo)
                # self.repo_combobox.setCurrentIndex(0)

    def validate(self) -> Tuple[bool, Optional[str]]:
        pat = self.pat_text.text()
        if pat == '':
            msg = _('Personal access token length should contain at '
                    'least 40 characters')
            return False, msg
        return True, None

    def create_repository(self, project_path: str):
        pat = self.pat_text.text()
        current_repo_index = self.repo_combobox.currentIndex()
        branch_idx = self.branch_combobox.currentIndex()
        repo = self.github_repo_model[current_repo_index - 1]
        branch = self.github_branch_model[branch_idx]

        clone_url = repo['clone_url']
        auth_method = 'x-access-token'
        callbacks = RemoteCallbacks(UserPass(auth_method, pat))
        new_path = osp.join(project_path, f'repo_clone_{int(time.time())}')
        clone_repository(clone_url, new_path,
                         checkout_branch=branch['name'],
                         callbacks=callbacks)

        for root, dirs, files in os.walk(new_path):
            plain_root = root.replace(new_path, project_path)
            for folder in dirs:
                os.makedirs(osp.join(plain_root, folder), exist_ok=True)
            for file in files:
                new_file_path = osp.join(plain_root, file)
                file_path = osp.join(root, file)
                shutil.copy2(file_path, new_file_path)

        shutil.rmtree(new_path, True)
