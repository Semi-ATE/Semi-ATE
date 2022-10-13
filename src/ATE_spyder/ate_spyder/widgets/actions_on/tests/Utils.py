from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import keyword


POWER = {'y': -24,
         'z': -21,
         'a': -18,
         'f': -15,
         'p': -12,
         'n': -9,
         'μ': -6,
         'm': -3,
         'c': -2,
         'd': -1,
         '˽': 0,
         '㍲': 1,
         'h': 2,
         'k': 3,
         'M': 6,
         'G': 9,
         'T': 12,
         'P': 15,
         'E': 18,
         'Z': 21,
         'Y': 24}


class Delegator(QtWidgets.QStyledItemDelegate):
    """General Custom Delegator Class that works with regex."""

    def __init__(self, regex, table=None, column=None, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.table: QtWidgets.QTableView = table
        self.column = column
        self.validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))

    def createEditor(self, parent, option, index):
        """Overloading to customize."""
        line_edit = QtWidgets.QLineEdit(parent)
        line_edit.setValidator(self.validator)
        line_edit.editingFinished.connect(lambda: self.validate_text(line_edit))

        return line_edit

    def validate_text(self, line_edit: QtWidgets.QLineEdit):
        if not keyword.iskeyword(line_edit.text()):
            return

        if self.table is None or self.column is None:
            return

        col = self.table.selectionModel().currentIndex().column()
        row = self.table.selectionModel().currentIndex().row()
        if col == self.column:
            item = self.table.model().item(row, col)
            item.setText("")
