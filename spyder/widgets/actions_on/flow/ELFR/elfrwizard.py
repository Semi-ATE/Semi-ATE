# -*- coding: utf-8 -*-
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase

quali_flow_name = "qualification_elfr_flow"
quali_flow_listentry_name = "ELFR"
quali_flow_tooltip = "Early Life Failure Rate (aka: BurnIn)"


class ELFRWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Duration (hours)", 0, 0, 500),
                intparam.IntParam("Temperature (°C)", 0, 0, 500),
                intparam.IntParam("VDD (V)", 0, 0, 500)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_name


def edit_item(storage, product: str):
    data = storage.get_unique_data_for_qualifcation_flow(quali_flow_name, product)
    dialog = ELFRWizard(data, storage)
    dialog.exec_()
    del(dialog)
