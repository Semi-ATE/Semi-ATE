# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase

quali_flow_name = "qualification_LU_flows"
quali_flow_listentry_name = "LU"
quali_flow_tooltip = "Latch-up"


class LUWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Class", 2, 0, 10),
                intparam.IntParam("Temperature (°C)", 150, 0, 200)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_listentry_name


def edit_item(storage, product: str):
    data = storage.get_unique_data_for_qualifcation_flow(quali_flow_listentry_name, product)
    dialog = LUWizard(data, storage)
    dialog.exec_()
    del(dialog)
