# -*- coding: utf-8 -*-
from ate_spyder.widgets.actions_on.flow.qualificationwizardbase.textboxparam import TextBoxParam


# The TextBoxParam represents a parameter that has a value
# and a name. It will generate a lineedit for dataentry
# end a label to show the name of the parameter. No validation
# is done on the input, except, that the parameter must not
# be empty
class WriteOnceTextParam(TextBoxParam):
    def load_values(self, src):
        if not src.has_attribute(self.name):
            self.inputBox.setText("")
        else:
            self.inputBox.setText(src.read_attribute(self.name))
            self.inputBox.setEnabled(False)
