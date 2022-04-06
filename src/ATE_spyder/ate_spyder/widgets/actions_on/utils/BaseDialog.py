from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import uic


class BaseDialog(QtWidgets.QDialog):
    def __init__(self, ui_file: str, parent: object):
        super().__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, on=False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, on=False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, on=False)
        self.ui_file = ui_file
        self._load_ui()

    def _load_ui(self):
        uic.loadUi(self.ui_file.replace('.py', '.ui'), self)
