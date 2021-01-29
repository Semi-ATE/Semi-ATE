from ATE.projectdatabase.FileOperator import FileOperator
from PyQt5 import QtWidgets
import ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.wizardbase
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase import wizardbase
from ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.textboxparam import TextBoxParam
from mock_db_object import MockDBObject


class TextParamWizard(wizardbase.wizardbase):
    def __init__(self):
        # self.parent = parent
        # Note: The init call needs to come after we setup this variable, in order for
        # it to exist when init calls _get_wizard_params
        self.theParam = TextBoxParam("Parameter1")
        super().__init__(MockDBObject(), None)

    def _get_wizard_parameters(self) -> list:
        return [self.theParam]

    def _get_wizard_testprogram_slots(self) -> dict:
        return []


def setup_method():
    def setup(test_func):
        def wrap(qtbot):
            window = TextParamWizard()
            qtbot.addWidget(window)
            return test_func(window, qtbot)
        return wrap
    return setup


@setup_method()
def test_textbox_param_can_find_line_edit(window, qtbot=None):
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert paramField is not None


@setup_method()
def test_textbox_param_line_edit_is_populated_with_default_value(window, qtbot=None):
    window.theParam.load_values(MockDBObject())
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert(paramField.text() == "")


@setup_method()
def test_textbox_param_line_edit_is_populated_from_inserted_data(window, qtbot):
    window.theParam.load_values(FileOperator._make_db_object({"Parameter1": "Foobar"}))
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    assert(paramField.text() == "Foobar")


@setup_method()
def test_textbox_param_empty_disables_save_button(window, qtbot):
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    paramField.setText("")
    saveButton = window.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    assert(saveButton.isEnabled() is False)


@setup_method()
def test_textbox_param_set_param_to_valid_value_enables_button(window, qtbot):
    paramField = window.findChild(QtWidgets.QLineEdit, "txtParameter1")
    paramField.setText("")
    saveButton = window.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    assert(saveButton.isEnabled() is False)
    qtbot.keyClicks(paramField, "Some Random Value")
    assert(saveButton.isEnabled() is True)


@setup_method()
def test_textbox_param_save_values_stores_value(window, qtbot):
    testParam = ATE.spyder.widgets.actions_on.flow.qualificationwizardbase.textboxparam.TextBoxParam("Parameter32")
    d = FileOperator._make_db_object({"Parameter32": "Some Value"})
    testParam.load_values(d)
    d2 = MockDBObject()
    testParam.store_values(d2)
    assert(d2.to_dict()["Parameter32"] == "Some Value")
