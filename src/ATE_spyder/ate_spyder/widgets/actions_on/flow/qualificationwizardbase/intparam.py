from ate_projectdatabase.FileOperator import DBObject
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase.textboxparam import TextBoxParam


# The IntParam represents a parameter consisting of a name, an
# integral value and an upper and lower bound. It will create
# a lineedit for dataentry and display the parameter name as well
# as the limits.
# All entered data is validated to check if...
# ... it can be converted into an int
# ... it is within the set limits.
# Upon deserialisation the parameter will reset to the provided
# default value, if it cannot deserialize itself from the
# respective data
class IntParam(TextBoxParam):

    def __init__(self, name, default: int, minval: int, maxval: int):
        super(IntParam, self).__init__(name)
        self.min = minval
        self.max = maxval
        self.default = default

    def create_ui_components(self, parent_container, on_change_handler):
        layout = super(IntParam, self).create_ui_components(parent_container, on_change_handler)
        self.unitTextField.setText(f"[{self.min}..{self.max}]")
        return layout

    # The validate method shall yield true, if the
    # data entered in the parameters fields is correct
    def _validate_impl(self) -> bool:
        try:
            tmp = int(self.inputBox.text())
            if tmp >= self.min and tmp <= self.max:
                return True
            else:
                return False
        except:
            return False

    def load_values(self, src: DBObject):
        if not src.has_attribute(self.name):
            self.inputBox.setText(str(self.default))
        else:
            try:
                self.inputBox.setText(str(int(src.read_attribute(self.name))))
            except:
                self.inputBox.setText(str(self.default))
