# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import writeoncetextparam
from ate_projectdatabase.FileOperator import FileOperator


quali_flow_name = "qualification_AC_flow"
quali_flow_listentry_name = "AC"
quali_flow_tooltip = "Autoclav"


class ACWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [writeoncetextparam.WriteOnceTextParam("name"),
                intparam.IntParam("MSL", 0, 0, 10000),
                intparam.IntParam("Bake Time (hours)", 0, 0, 500),
                intparam.IntParam("Bake Temperature (°C)", 0, 0, 500),
                intparam.IntParam("Soak Time (hours)", 0, 0, 500),
                intparam.IntParam("Soak Temperature (°C)", 12, 0, 500),
                intparam.IntParam("Soak relative humidity (%)", 0, 0, 100),
                intparam.IntParam("Num Reflows", 0, 0, 500),
                intparam.IntParam("Reflow Temperature (°C)", 12, 0, 500)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name


def new_item(storage, product: str):
    dialog = ACWizard(FileOperator._make_db_object({"product": product}), storage)
    dialog.exec_()
    del(dialog)


def edit_item(storage, data):
    dialog = ACWizard(data, storage)
    dialog.exec_()
    del(dialog)


def view_item(storage, data):
    dialog = ACWizard(data, storage)
    dialog.set_view_only()
    dialog.exec_()
    del(dialog)
