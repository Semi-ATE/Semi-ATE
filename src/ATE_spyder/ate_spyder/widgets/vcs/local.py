# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Local Git repository initialization.
"""

# Standard library imports
import re
import os
import socket
from typing import Optional, Tuple

# Qt imports
from qtpy.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout

# Third-party imports
from pygit2 import (
    init_repository, Repository, Signature, reference_is_valid_name)
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.vcs import VCSInitializationProvider

# Localization
_ = get_translation('spyder')

GIT_BRANCH_NAME = re.compile(
    r'^(?!/|.*([/.]\.|//|@\{|\\\\))[^\040\177 ~^:?*\[]+$')


class LocalGitProvider(VCSInitializationProvider):
    """Project configuration widget used to create a local git repository."""

    NAME = 'local_git'
    RANK = 1

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Branch name
        branch_label = QLabel(_('Default branch name'))
        self.branch_text = QLineEdit()
        self.branch_text.setText('main')
        self.branch_text.textChanged.connect(
            lambda _: self.sig_widget_changed.emit())

        author_label = QLabel(_('Commit author name'))
        username = os.environ.get('USER', os.environ.get('USERNAME'))
        self.author_text = QLineEdit()
        self.author_text.setText(username)
        self.author_text.textChanged.connect(
            lambda _: self.sig_widget_changed.emit())

        email_label = QLabel(_('Email address'))
        self.email_text = QLineEdit()
        hostname = socket.gethostname()
        email = f'{username}@{hostname}'
        self.email_text.setText(email)

        self.email_text.textChanged.connect(
            lambda _: self.sig_widget_changed.emit())

        branch_layout = QHBoxLayout()
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_text)

        author_layout = QHBoxLayout()
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_text)

        email_layout = QHBoxLayout()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_text)

        layout = QVBoxLayout()
        layout.addLayout(branch_layout)
        layout.addLayout(author_layout)
        layout.addLayout(email_layout)
        self.setLayout(layout)

    @classmethod
    def get_name(cls) -> str:
        return _('Local (Git)')

    def create_repository(self, project_path: str):
        branch_name = self.branch_text.text()
        author = self.author_text.text()
        email = self.email_text.text()

        repo: Repository = init_repository(
            project_path, initial_head=branch_name)

        # Create initial commit
        index = repo.index
        index.add_all()
        index.write()
        tree = index.write_tree()
        me = Signature(author, email)
        repo.create_commit("HEAD", me, me, "commit msg", tree, [])

        _, ref = repo.resolve_refish(branch_name)
        repo.checkout(ref)

    def validate(self) -> Tuple[bool, Optional[str]]:
        branch_name = self.branch_text.text()
        is_valid = GIT_BRANCH_NAME.match(branch_name) is not None
        # is_valid = reference_is_valid_name(branch_name)
        msg = []
        if not is_valid:
            msg.append((f'branch name {repr(branch_name)} is not a valid '
                        'git reference name, see git-check-ref-format to '
                        'get more information'))

        author_name = self.author_text.text()
        if author_name == '':
            msg.append('the author name must be non-empty')
            is_valid = False

        email = self.email_text.text()
        if email == '':
            msg.append('the email must be non-empty')
            is_valid = False

        msg = ' and '.join(msg).strip().capitalize()
        return is_valid, msg
