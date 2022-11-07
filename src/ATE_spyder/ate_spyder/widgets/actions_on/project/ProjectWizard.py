'''
Created on Nov 18, 2019

@author: hoeren
'''

# Standard library imports
import os
import re
import os.path as osp
from pathlib import Path
from typing import Optional, Dict, Type, List

# Qt-related imports
import qtawesome as qta
from qtpy.QtCore import Qt, Signal, QAbstractListModel, QObject, QModelIndex
from qtpy.QtWidgets import (QDialog, QWidget, QVBoxLayout, QLabel, QLineEdit,
                            QHBoxLayout, QComboBox, QDialogButtonBox,
                            QGroupBox, QCheckBox, QStackedWidget)

# Third-party imports
from spyder.api.translations import get_translation

# Local imports
from ate_spyder.widgets.constants import QualityGrades
from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_name_regex
from ate_spyder.widgets.vcs import VCSInitializationProvider

# Localization
_ = get_translation('spyder')


class VCSInitializationModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None,
                 vcs_providers: List[
                    VCSInitializationProvider] = None) -> None:
        super().__init__(parent)
        self.vcs_providers = vcs_providers

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str:
        if role == Qt.DisplayRole:
            vcs_prov = self.vcs_providers[index.row()]
            return vcs_prov.get_name()

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.vcs_providers)

    def __getitem__(self, index: int) -> VCSInitializationProvider:
        return self.vcs_providers[index]


class ProjectWizard(QDialog):
    """Create new project dialog."""
    sig_create_new_project = Signal(bool, dict)
    sig_dialog_enabled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None,
                 vcs_providers: Dict[
                    str, Type[VCSInitializationProvider]] = None,
                 project_info=None,
                 project_path: str = None) -> None:
        super().__init__(parent)
        self.project_info = project_info
        self.project_path = project_path

        # Setup dialog information
        self.setWindowTitle(_('New ATE Project Wizard'))

        # Project name group
        project_name_label = QLabel(_('Project Name:'))
        self.project_text = QLineEdit(self)
        project_name_layout = QHBoxLayout()
        project_name_layout.addWidget(project_name_label)
        project_name_layout.addWidget(self.project_text)

        # Quality grade group
        quality_grades = QualityGrades.translations
        quality_label = QLabel(_('Quality grade:'))
        self.quality_combo = QComboBox()
        self.quality_combo.insertItems(0, quality_grades)
        self.quality_combo.setToolTip(_('Indicate Base Grade of the project'))

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)

        # VCS configuration
        vcs_label = QLabel(_('This project will use version control'))
        self.vcs_checkbox = QCheckBox()

        vcs_label_layout = QHBoxLayout()
        vcs_label_layout.addWidget(vcs_label)
        vcs_label_layout.addWidget(self.vcs_checkbox)

        # VCS providers filtering ans sorting
        sorted_vcs_providers = [(vcs_providers[p], vcs_providers[p].RANK)
                                for p in vcs_providers]
        sorted_vcs_providers = sorted(
            sorted_vcs_providers, key=lambda x: x[1])
        sorted_vcs_providers = [x[0] for x in sorted_vcs_providers]

        self.vcs_prov_model = VCSInitializationModel(
            self, sorted_vcs_providers)

        # VCS initialization group
        vcs_group = QGroupBox('Version control settings')
        vcs_group_layout = QVBoxLayout()

        vcs_prov_label = QLabel(_('Initialize using'))
        self.vcs_prov_combo = QComboBox()

        self.vcs_stack = QStackedWidget()
        self.vcs_conf_widget: Optional[VCSInitializationProvider] = None

        vcs_group_layout.addWidget(vcs_prov_label)
        vcs_group_layout.addWidget(self.vcs_prov_combo)
        vcs_group_layout.addWidget(self.vcs_stack)
        vcs_group.setLayout(vcs_group_layout)

        # Feedback label
        self.feedback_label = QLabel()

        # Dialog layout
        layout = QVBoxLayout()
        layout.addLayout(project_name_layout)
        layout.addLayout(quality_layout)
        layout.addLayout(vcs_label_layout)
        layout.addWidget(vcs_group)
        layout.addWidget(self.feedback_label)
        self.setLayout(layout)

        # Signals and configuration
        self.add_button_box(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.vcs_checkbox.toggled.connect(vcs_group.setEnabled)
        self.vcs_checkbox.toggled.connect(lambda _: self.validate())
        self.vcs_checkbox.setChecked(True)

        self.vcs_prov_combo.currentIndexChanged.connect(self.provider_changed)
        self.vcs_prov_combo.setModel(self.vcs_prov_model)

        self.project_text.textChanged.connect(lambda _: self.validate())
        self.project_text.setText(osp.basename(project_path))
        self.validate()

    def add_button_box(self, stdbtns):
        """Create dialog button box and add it to the dialog layout"""
        self.bbox = QDialogButtonBox(stdbtns)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(self.bbox)
        self.layout().addLayout(btnlayout)

        ok_button = self.bbox.button(QDialogButtonBox.Ok)
        self.cancel_button = self.bbox.button(QDialogButtonBox.Cancel)
        self.ok_button = ok_button
        self.sig_dialog_enabled.connect(ok_button.setEnabled)

    def provider_changed(self, index: int):
        if index < 0:
            return

        # Clear the QStackWidget contents
        self.vcs_conf_widget = None
        while self.vcs_stack.count() > 0:
            widget = self.vcs_stack.widget(0)
            self.vcs_stack.removeWidget(widget)

        ProviderWidget = self.vcs_prov_model[index]
        self.vcs_conf_widget: VCSInitializationProvider = ProviderWidget()
        self.vcs_conf_widget.sig_widget_changed.connect(self.validate)
        self.vcs_conf_widget.sig_update_status.connect(self.change_status)
        self.vcs_stack.addWidget(self.vcs_conf_widget)
        self.validate()

    def validate(self):
        is_valid = True
        check_vcs = self.vcs_checkbox.isChecked()
        self.feedback_label.setText('')

        # Validate project name
        project_name = self.project_text.text()
        if not re.match(valid_name_regex, project_name):
            self.feedback_label.setText('Project name is invalid')
            is_valid = False

        # Validate VCS widget
        if check_vcs and self.vcs_conf_widget is not None:
            self.vcs_conf_widget.set_ate_project_name(project_name)
            vcs_valid, msg = self.vcs_conf_widget.validate()
            if not vcs_valid:
                feedback_text = msg
                if not is_valid:
                    feedback_text = self.feedback_label.text()
                    feedback_text = f'{feedback_text} and {msg}'
                self.feedback_label.setText(feedback_text)
            is_valid = is_valid and vcs_valid

        self.sig_dialog_enabled.emit(is_valid)

    def change_status(self, is_valid: bool, msg: Optional[str]):
        self.sig_dialog_enabled.emit(is_valid)
        text = ''
        if msg is not None:
            text = msg
        self.feedback_label.setText(text)

    def accept(self) -> None:
        check_vcs = self.vcs_checkbox.isChecked()
        if check_vcs and self.vcs_conf_widget is not None:
            self.vcs_conf_widget.create_repository(self.project_path)

        project_name = self.project_text.text()
        new_path = Path(osp.dirname(self.project_path)).joinpath(project_name)
        cur_path = Path(self.project_path)

        if cur_path != new_path:
            cur_path.rename(new_path)

        self.project_info(str(new_path))
        # config step shall be done first after the re-initialization
        # of the project_info is done
        configuration = self._get_current_configuration()
        print(configuration)
        self.project_info.add_settings(
            quality_grade=configuration['quality_grade']
        )
        self.setResult(QDialog.Accepted)
        return super().accept()

    def _get_current_configuration(self):
        translation = self.quality_combo.currentText()
        enum_value = QualityGrades[translation]
        return {
            'quality_grade': enum_value
        }
