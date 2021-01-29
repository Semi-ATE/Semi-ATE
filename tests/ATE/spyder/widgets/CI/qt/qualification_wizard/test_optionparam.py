from ATE.projectdatabase.FileOperator import FileOperator
from PyQt5 import QtWidgets
import ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.wizardbase
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.optionparam import OptionParam
from mock_db_object import MockDBObject


class OptionParamWizard(wizardbase.wizardbase):
    def __init__(self):
        # self.parent = parent
        # Note: The init call needs to come after we setup this variable, in order for
        # it to exist when init calls _get_wizard_params
        self.theParam = OptionParam("Parameter1", ["ChoiceA", "ChoiceB", "ChoiceC"])
        super().__init__(MockDBObject(), None)

    def _get_wizard_parameters(self) -> list:
        return [self.theParam]

    def _get_wizard_testprogram_slots(self) -> dict:
        return []


def setup_method():
    def setup(test_func):
        def wrap(qtbot):
            window = OptionParamWizard()
            qtbot.addWidget(window)
            return test_func(window, qtbot)
        return wrap
    return setup


@setup_method()
def test_option_param_can_find_combobox(window, qtbot=None):
    paramField = window.findChild(QtWidgets.QComboBox, "cbParameter1")
    assert paramField is not None


@setup_method()
def test_textbox_param_line_edit_is_populated_with_default_value(window, qtbot=None):
    window.theParam.load_values(MockDBObject())
    paramField = window.findChild(QtWidgets.QComboBox, "cbParameter1")
    assert(paramField.currentText() == "ChoiceA")


@setup_method()
def test_textbox_param_line_edit_is_populated_from_inserted_data(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "ChoiceB"}))
    paramField = window.findChild(QtWidgets.QComboBox, "cbParameter1")
    assert(paramField.currentText() == "ChoiceB")


@setup_method()
def test_int_param_save_values_stores_value(window, qtbot):
    testParam = ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.optionparam.OptionParam("Parameter32", ["A", "B", "C"])
    d = FileOperator._make_db_object({"Parameter32": "C"})
    testParam.load_values(d)
    d2 = MockDBObject()
    testParam.store_values(d2)
    assert(d2.to_dict()["Parameter32"] == "C")
