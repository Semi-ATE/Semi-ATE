# -*- coding: utf-8 -*-
from ATE.org.actions_on.flow.qualificationwizardbase.textboxparam import TextBoxParam


# The TextBoxParam represents a parameter that has a value
# and a name. It will generate a lineedit for dataentry
# end a label to show the name of the parameter. No validation
# is done on the input, except, that the parameter must not
# be empty
class WriteOnceTextParam(TextBoxParam):
    def load_values(self, src):
        if self.name not in src:
            self.inputBox.setText("")
        else:
            self.inputBox.setText(src[self.name])
            self.inputBox.setEnabled(False)
