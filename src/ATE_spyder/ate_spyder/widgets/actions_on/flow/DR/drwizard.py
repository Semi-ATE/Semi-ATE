# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import writeoncetextparam
from ate_projectdatabase.FileOperator import FileOperator


quali_flow_name = "qualification_DR_flows"
quali_flow_listentry_name = "DR"
quali_flow_tooltip = "Data Retention"


class DRWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [writeoncetextparam.WriteOnceTextParam("name"),
                intparam.IntParam("Length (hours)", 0, 0, 10000),
                intparam.IntParam("Temperature (C°)", 0, 0, 100)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name


def new_item(storage, product: str):
    dialog = DRWizard(FileOperator._make_db_object({"product": product}), storage)
    dialog.exec_()
    del(dialog)


def edit_item(storage, data):
    dialog = DRWizard(data, storage)
    dialog.exec_()
    del(dialog)


def view_item(storage, data):
    dialog = DRWizard(data, storage)
    dialog.set_view_only()
    dialog.exec_()
    del(dialog)
