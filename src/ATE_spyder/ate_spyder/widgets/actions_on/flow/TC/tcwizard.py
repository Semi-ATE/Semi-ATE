# -*- coding: utf-8 -*-

from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase import intparam
from PyQt5 import QtWidgets


quali_flow_name = "qualification_tc_flow"
quali_flow_listentry_name = "TC"
quali_flow_tooltip = "Temperature Cycling"


class TCWizard(wizardbase.wizardbase):
    # This function shall return a list of parameters, that
    # is usable by the wizard.
    def _get_wizard_parameters(self) -> list:
        return [intparam.IntParam("Cycles", 0, 0, 10000),
                intparam.IntParam("Temperature (lowerbound) (°C)", 0, 0, 100),
                intparam.IntParam("Temperature (upperbound) (°C)", 0, 0, 100),
                intparam.IntParam("Duration (Days)", 0, 0, 365)]

    # This function shall return a list of testprogram slots
    # Note: We expect a list of TextBoxParams here
    def _get_wizard_testprogram_slots(self) -> list:
        return []

    def _get_data_type(self) -> str:
        return quali_flow_listentry_name


def edit_item(storage, product: str):
    data = storage.get_unique_data_for_qualifcation_flow(quali_flow_listentry_name, product)
    dialog = TCWizard(data, storage)
    dialog.exec_()
    del(dialog)


if __name__ == '__main__':
    import sys, qdarkstyle

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    dialog = TCWizard(dict(), None)
    dialog.show()
    sys.exit(app.exec_())
