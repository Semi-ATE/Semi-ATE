# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import optionparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import writeoncetextparam
from ate_projectdatabase.FileOperator import FileOperator

quali_flow_name = "qualification_HTOL_flow"
quali_flow_listentry_name = "HTOL"
quali_flow_tooltip = "High Temperature Operating Life"


class HTOLWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [writeoncetextparam.WriteOnceTextParam("name"),
                optionparam.OptionParam("Reference Measurement", self._get_possible_references()),
                intparam.IntParam("Temperature (°C)", 0, 0, 200),
                intparam.IntParam("Length (hours)", 0, 0, 10000),
                intparam.IntParam("Testwindow (hours)", 0, 0, 500),
                intparam.IntParam("Vdd (V)", 12, 0, 240)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name

    def _get_possible_references(self) -> []:
        htols = self.storage.get_data_for_qualification_flow(self._get_data_type(), self.datasource.product)
        usedHtols = ["ZHM"]
        for htol in htols:
            if self.datasource.has_attribute("name"):
                if htol.name == self.datasource.name:
                    continue
            usedHtols.append(htol.name)
        return usedHtols


def new_item(storage, product: str):
    dialog = HTOLWizard(FileOperator._make_db_object({"product": product}), storage)
    dialog.exec_()
    del(dialog)


def edit_item(storage, data):
    print(data)
    dialog = HTOLWizard(data, storage)
    dialog.exec_()
    del(dialog)


def view_item(storage, data):
    dialog = HTOLWizard(data, storage)
    dialog.set_view_only()
    dialog.exec_()
    del(dialog)


def check_delete_constraints(storage, data):
    # Constraints for deleting a HTOL entry:
    # No other HTOL entries may refer to it.
    htols = storage.get_data_for_qualification_flow(quali_flow_name, storage.active_target)
    for htol in htols:
        if htol.read_attribute("Reference Measurement") == data.name:
            dependencyName = data.name
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Cannot delete HTOL Entry {dependencyName}. The HTOL entry {htol.name} depends on it.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return False
    return True
