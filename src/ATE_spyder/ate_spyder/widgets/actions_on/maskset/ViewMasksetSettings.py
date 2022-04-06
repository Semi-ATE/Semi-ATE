from enum import Enum

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.maskset.constants import DEFINITION
from ate_spyder.widgets.actions_on.maskset.constants import PAD_INFO
from ate_spyder.widgets.actions_on.maskset.NewMasksetWizard import NewMasksetWizard


class ErrorMessage(Enum):
    NoValidConfiguration = "no valid configuration"
    InvalidConfigurationElements = "configuration does not match the template inside constants.py"

    def __call__(self):
        return self.value


class ViewMasksetSettings(NewMasksetWizard):
    def __init__(self, project_info, maskset_name):
        super().__init__(project_info, read_only=True)
        self.maskset_name = maskset_name
        self._setup_item(self.maskset_name)
        ViewMasksetSettings._setup_dialog_fields(self, self.maskset_name)

    def _setup_item(self, maskset_name):
        self.setWindowTitle("Maskset Setting")

        self.masksetName.setText(maskset_name)
        self.masksetName.setEnabled(False)
        self.bondpads.setEnabled(False)
        self.waferDiameter.setEnabled(False)
        self.dieSizeX.setEnabled(False)
        self.dieSizeY.setEnabled(False)
        self.scribeX.setEnabled(False)
        self.scribeY.setEnabled(False)
        self.dieRefY.setEnabled(False)
        self.dieRefX.setEnabled(False)
        self.xOffset.setEnabled(False)
        self.yOffset.setEnabled(False)
        self.flat.setEnabled(False)
        self.Type.setEnabled(False)
        self.editWaferMapButton.setEnabled(False)
        self.importFor.setEnabled(False)
        self.viewDieButton.setEnabled(False)
        self.customer.setEnabled(False)

    @staticmethod
    def _init_table(dialog, table_size, enable_edit):
        dialog.bondpadTable.setRowCount(table_size)
        row = dialog.bondpadTable.rowCount()
        column = dialog.bondpadTable.columnCount()
        for r in range(row):
            for c in range(column):
                item = QtWidgets.QTableWidgetItem('')
                dialog.bondpadTable.setItem(r, c, item)
                item.setFlags(QtCore.Qt.NoItemFlags)
                if c == 0:
                    item.setTextAlignment(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
                else:
                    item.setTextAlignment(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))

        # resize cell columns
        for c in range(dialog.bondpadTable.columnCount()):
            if c == PAD_INFO.PAD_NAME_COLUMN():
                dialog.bondpadTable.setColumnWidth(c, PAD_INFO.NAME_COL_SIZE())

            elif c in (PAD_INFO.PAD_POS_X_COLUMN(), PAD_INFO.PAD_POS_Y_COLUMN(), PAD_INFO.PAD_SIZE_X_COLUMN(), PAD_INFO.PAD_SIZE_Y_COLUMN(), PAD_INFO.PAD_TYPE_COLUMN()):
                dialog.bondpadTable.setColumnWidth(c, PAD_INFO.REF_COL_SIZE())

            elif c == PAD_INFO.PAD_DIRECTION_COLUMN():
                dialog.bondpadTable.setColumnWidth(c, PAD_INFO.DIR_COL_SIZE())

        dialog.bondpadTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        dialog.bondpadTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        dialog.bondpadTable.setEnabled(enable_edit)

    @staticmethod
    def is_valid_configuration(maskset_configuration):
        if not maskset_configuration.keys() == DEFINITION.keys():
            return False

        return True

    @staticmethod
    def _setup_dialog_fields(dialog, maskset_name, enable_edit=False):
        maskset_configuration = dialog.project_info.get_maskset_definition(maskset_name)
        maskset_customer = dialog.project_info.get_maskset_customer(maskset_name)
        if not ViewMasksetSettings.is_valid_configuration(maskset_configuration):
            dialog.feedback.setText(ErrorMessage.InvalidConfigurationElements())
            dialog.feedback.setStyleSheet('color: orange')
            return

        ViewMasksetSettings._init_table(dialog, len(maskset_configuration['BondpadTable']), enable_edit)

        if maskset_customer:
            dialog.Type.setCurrentIndex(1)
            dialog.customer.setText(maskset_customer)
        else:
            dialog.Type.setCurrentIndex(0)

        dialog.feedback.setText('')

        index = dialog.waferDiameter.findText(str(maskset_configuration["WaferDiameter"]), QtCore.Qt.MatchFixedString)
        if index >= 0:
            dialog.waferDiameter.setCurrentIndex(index)

        dialog.masksetName.setText(maskset_name)
        dialog.masksetName.setEnabled(False)

        dialog.bondpads.setValue((maskset_configuration["Bondpads"]))

        dialog.dieSizeX.setText(str(maskset_configuration["DieSize"][0]))  # tuple
        dialog.dieSizeY.setText(str(maskset_configuration["DieSize"][1]))

        dialog.dieRefX.setText(str(maskset_configuration["DieRef"][0]))  # tuple
        dialog.dieRefY.setText(str(maskset_configuration["DieRef"][1]))

        dialog.scribeX.setText(str(maskset_configuration["Scribe"][0]))  # tuple
        dialog.scribeY.setText(str(maskset_configuration["Scribe"][1]))

        dialog.xOffset.setText(str(maskset_configuration["Offset"][0]))  # tuple
        dialog.yOffset.setText(str(maskset_configuration["Offset"][1]))

        table_infos = maskset_configuration["BondpadTable"]
        dialog.bondpadTable.setRowCount(len(table_infos))
        row = dialog.bondpadTable.rowCount()
        column = dialog.bondpadTable.columnCount()

        for r in range(row):
            for c in range(column):
                dialog.bondpadTable.item(r, c).setText(str(table_infos[r][c]))

        dialog.OKButton.setEnabled(True)
        dialog._validate_table()

    def OKButtonPressed(self):
        self.accept()


def display_maskset_settings_dialog(project_info, maskset_name):
    maskset_wizard = ViewMasksetSettings(project_info, maskset_name)
    maskset_wizard.exec_()
    del(maskset_wizard)
