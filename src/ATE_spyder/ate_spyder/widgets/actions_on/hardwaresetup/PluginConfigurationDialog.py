# -*- coding: utf-8 -*-
import re

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog


class PluginConfigurationDialog(BaseDialog):

    def __init__(self, parent, object_name, config_items, hardware, project_info, current_config, read_only):
        super().__init__(__file__, parent)
        self.project_info = project_info
        self.object_name = object_name
        self.target_hardware = hardware
        self.cfg = {}

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', self.__class__.__name__)))
        saveButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        saveButton.clicked.connect(self.__store_data)
        cancelButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        cancelButton.clicked.connect(self.accept)

        # if and only if not values were passed as current values, attempt to load from disc:
        if current_config is None:
            values_to_display = self.project_info.load_plugin_cfg(hardware, self.object_name)
        else:
            values_to_display = current_config

        self.input_data = {}
        layout = QtWidgets.QVBoxLayout()

        for p in config_items:
            self.create_ui_components(layout, p, values_to_display, read_only)

        layout.insertStretch(len(config_items), 0)
        self.grpParams.setLayout(layout)
        self.grpParams.setTitle(f"Parameters for {self.object_name}")
        self.show()

    def create_ui_components(self, parent_container, param_name, values_to_display, read_only):
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        textField = QtWidgets.QLabel()
        textField.setObjectName(f"{param_name}_label")
        textField.setText(param_name)
        textField.setMaximumWidth(64)
        textField.setFixedWidth(64)
        layout.addWidget(textField)

        # Append Input box
        inputBox = QtWidgets.QLineEdit()
        inputBox.setObjectName(f"{param_name}_value")
        inputBox.setMaximumWidth(256)
        inputBox.setAlignment(QtCore.Qt.AlignLeft)
        if param_name in values_to_display:
            inputBox.setText(values_to_display.get(param_name))

        if read_only:
            inputBox.setEnabled(False)

        layout.addWidget(inputBox)
        self.input_data[param_name] = inputBox

        layout.insertStretch(1)
        parent_container.addLayout(layout)
        return layout

    def __store_data(self):
        output_values = {}
        for param_name, input_box in self.input_data.items():
            output_values[param_name] = input_box.text()

        self.cfg = output_values
        self.accept()

    def get_cfg(self):
        return self.cfg
