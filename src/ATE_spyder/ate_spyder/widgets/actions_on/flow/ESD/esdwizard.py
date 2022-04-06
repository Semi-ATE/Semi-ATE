# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import optionparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_projectdatabase.FileOperator import FileOperator


quali_flow_name = "qualification_esd_flow"
quali_flow_listentry_name = "ESD"
quali_flow_tooltip = "Electrostatic Discharge"


class ESDWizard(wizardbase.wizardbase):
    def __init__(self, datasource: dict, storage):
        super(ESDWizard, self).__init__(datasource, storage)

    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Voltage Corner Leads (V)", 750, 0, 2000),
                intparam.IntParam("Voltage Other Leads (V)", 500, 0, 2000)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _custom_parameter_setup(self):
        self.modelChooser = optionparam.OptionParam("Model", ["HBM", "CDM"])
        layout = QtWidgets.QVBoxLayout()
        self.modelChooser.create_ui_components(layout, self.__on_esd_model_changed)
        self.grpESDModelChooser.setLayout(layout)
        self.__on_esd_model_changed()

    def __on_esd_model_changed(self):
        showParamBox = self.modelChooser.get_selection() == "CDM"
        self.grpParams.setVisible(showParamBox)

    def _get_data_type(self) -> str:
        return quali_flow_name

    def _custom_store_data(self, dst: dict):
        self.modelChooser.store_values(dst)
        dst["name"] = self.modelChooser.get_selection()

    def _custom_load_data(self, src: dict):
        self.modelChooser.load_values(src.get_definition())

    def set_view_only(self):
        super().set_view_only()
        self.modelChooser.disable_ui_components()

    def get_ui_file(self) -> str:
        return __file__.replace('.py', '.ui')


def edit_item(storage, data):
    dialog = ESDWizard(data, storage)
    dialog.exec_()
    del(dialog)


def new_item(storage, product: str):
    dialog = ESDWizard(FileOperator._make_db_object({"product": product}), storage)
    dialog.exec_()
    del(dialog)


def view_item(storage, data):
    dialog = ESDWizard(data, storage)
    dialog.set_view_only()
    dialog.exec_()
    del(dialog)


if __name__ == '__main__':
    import sys, qdarkstyle

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    dialog = ESDWizard(dict(), None)
    dialog.show()
    sys.exit(app.exec_())
