# -*- coding: utf-8 -*-

from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam

quali_flow_name = "qualification_hast_flow"
quali_flow_listentry_name = "HAST"
quali_flow_tooltip = "Highly Accelerated Stress Test"


class HASTWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Testwindow (hours)", 0, 0, 10000),
                intparam.IntParam("Duration (hours)", 0, 0, 100),
                intparam.IntParam("Temperature (°C)", 0, 0, 100),
                intparam.IntParam("Rel. Humidity (%)", 0, 0, 100)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name


def edit_item(storage, product: str):
    data = storage.get_unique_data_for_qualifcation_flow(quali_flow_name, product)
    dialog = HASTWizard(data, storage)
    dialog.exec_()
    del(dialog)
