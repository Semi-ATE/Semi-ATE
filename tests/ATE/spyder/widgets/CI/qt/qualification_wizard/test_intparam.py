import ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.wizardbase
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.intparam import IntParam
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ATE.projectdatabase.FileOperator import FileOperator

from mock_db_object import MockDBObject
from PyQt5 import QtWidgets


class IntParamWizard(wizardbase.wizardbase):
    def __init__(self):
        # self.parent = parent
        # Note: The init call needs to come after we setup this variable, in order for
        # it to exist when init calls _get_wizard_params
        self.theParam = IntParam("Parameter1", 17, 10, 20)
        super().__init__(MockDBObject(), None)

    def _get_wizard_parameters(self) -> list:
        return [self.theParam]

    def _get_wizard_testprogram_slots(self) -> dict:
        return []


def setup_method():
    def setup(test_func):
        def wrap(qtbot):
            window = IntParamWizard()
            qtbot.addWidget(window)
            return test_func(window, qtbot)
        return wrap
    return setup


@setup_method()
def test_int_param_can_find_line_edit(window, qtbot=None):
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert paramField is not None


@setup_method()
def test_int_param_line_edit_is_populated_with_default_value(window, qtbot=None):
    window.theParam.load_values(MockDBObject())
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert(paramField.text() == "17")


@setup_method()
def test_int_param_line_edit_is_populated_from_inserted_data(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "20"}))
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert(paramField.text() == "20")


@setup_method()
def test_int_param_line_edit_is_set_to_default_if_data_is_invalid(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "I Am Invalid"}))
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert(paramField.text() == "17")


@setup_method()
def test_int_param_invalid_value_disables_save_button(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "9"}))
    saveButton = window.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    assert(saveButton.isEnabled() is False)


@setup_method()
def test_int_param_set_param_to_valid_value_enables_button(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "9"}))
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    saveButton = window.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    assert(saveButton.isEnabled() is False)
    paramField.setText("")
    assert(saveButton.isEnabled() is False)
    qtbot.keyClicks(paramField, "20")
    assert(paramField.text() == "20")
    assert(saveButton.isEnabled() is True)


@setup_method()
def test_int_param_save_values_stores_value(window, qtbot):
    testParam = ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.intparam.IntParam("Parameter32", 17, 10, 20)
    d = FileOperator._make_db_object({"Parameter32": "15"})
    testParam.load_values(d)
    d2 = MockDBObject()
    testParam.store_values(d2)
    assert(d2.to_dict()["Parameter32"] == "15")
