# -*- coding: utf-8 -*-
import re

from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog


# wizardbase is the baseclass for qualification wizards.
# It serves as a generic ui to host parameter entry, editing
# and storing
class wizardbase(BaseDialog):

    def __init__(self, datasource, storage):
        super().__init__(__file__, storage.parent if storage else None)
        # The dialog always works on a given set of data.
        # This can be either new data (in this case datasource
        # is an empty dict), or data from the database (in this
        # case datasource is populated with data that matches
        # the data used by the dialog.)
        # The dialog will modify the provided data, persisting
        # the data has to be done by the calling code that
        # generated the data in the first place.
        self.datasource = datasource
        self.storage = storage
        self.enable_save = True
        self.setup_parameters()

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', self.__class__.__name__)))
        saveButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        saveButton.clicked.connect(self.__store_data)

        cancelButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        cancelButton.clicked.connect(self.accept)

        self.__load_data(self.datasource)
        self.__on_any_parameter_change()
        self.show()

    def set_view_only(self):
        self.enable_save = False
        saveButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        saveButton.setEnabled(False)
        for p in self.wizard_parameters:
            p.disable_ui_components()

    def setup_parameters(self):
        self.wizard_parameters = self._get_wizard_parameters()

        # Create controls for wizard parameters
        self.grpParams.setTitle("Parameters")
        layout = QtWidgets.QVBoxLayout()
        for p in self.wizard_parameters:
            p.create_ui_components(layout, self.__on_any_parameter_change)
        self.grpParams.setLayout(layout)

        layout.insertStretch(len(self.wizard_parameters), 0)

        self._custom_parameter_setup()

    def _custom_parameter_setup(self):
        pass

    # The edit functions of all parameters are wired to this cb.
    # We use the cb to validate the whole form, i.e.: Check that all
    # params are set to valid values. If so, we enable the Ok Button.
    # Otherwise it is disabled
    def __on_any_parameter_change(self):
        allgood = True
        allgood = all(x.validate() for x in self.wizard_parameters)
        saveButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        saveButton.setEnabled(allgood and self.enable_save)

    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return []

    # This function is called after all defined parameters
    # of the dialog have been serialized into dst.
    # Override this method if additional actions need
    # to be done during storing.
    def _custom_store_data(self, dst: dict):
        pass

    # This function is called after all defined parameters
    # of the dialog have been deserialized from src.
    # Override this method if additional actions need
    # to be done during loading.
    def _custom_load_data(self, src: dict):
        pass

    def _get_data_type(self) -> str:
        return self.__class__.__name__

    def __store_data(self):
        # Note: Most qflows have only a single instance per
        #       project per product (?). In these cases we can
        #       generate a name based on the wizard type,
        #       that we put into the data here.
        #       QFlows that have multiple instances and
        #       allow free naming shall overwrite the
        #       'name' value with a parameter. or in
        #       the "_custom_store_data" method
        self.datasource.write_attribute("name", self.__class__.__name__)
        self.datasource.write_attribute("type", self._get_data_type())

        for x in self.wizard_parameters:
            x.store_values(self.datasource)

        self._custom_store_data(self.datasource)

        self.storage.add_or_update_qualification_flow_data(self.datasource)
        self.accept()

    def __load_data(self, src: dict):
        for x in self.wizard_parameters:
            x.load_values(src)
        self._custom_load_data(src)
