# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase

quali_flow_name = "qualification_thb_flow"
quali_flow_listentry_name = "THB"
quali_flow_tooltip = "Temperature Humidity Bias"


class THBWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Testwindow (hours)", 0, 0, 400),
                intparam.IntParam("Duration (hours)", 0, 0, 10000),
                intparam.IntParam("Temperature (°C)", 0, 0, 100),
                intparam.IntParam("Rel. Humidity (%)", 0, 0, 100),
                intparam.IntParam("VDD (V)", 12, 0, 120)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name


def edit_item(storage, product: str):
    data = storage.get_unique_data_for_qualifcation_flow(quali_flow_name, product)
    dialog = THBWizard(data, storage)
    dialog.exec_()
    del(dialog)
