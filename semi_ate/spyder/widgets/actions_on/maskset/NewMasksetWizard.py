'''
Created on Nov 20, 2019

@author: hoeren
'''

import os
import re

from PyQt5 import QtCore, QtGui, QtWidgets

import qtawesome as qta

from ATE.org.validation import is_valid_maskset_name

from ATE.org.actions_on.maskset.constants import PAD_INFO, DEFAULT_ROW, PadType, PadDirection, PadStandardSize

from ATE.org.plugins.pluginmanager import get_plugin_manager
from ATE.org.actions_on.utils.BaseDialog import BaseDialog

standard_flat_height = 7  # mm
standard_scribe = 100  # um


class NewMasksetWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__)
        self.plugin_manager = get_plugin_manager()
        self.plugin_names = []
        self.prev_item = None

        self.is_table_enabled = False
        self.selected_cell = None
        self.read_only = read_only
        self.is_active = True
        self.project_info = project_info
        self._setup()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        from ATE.org.validation import valid_positive_integer_regex
        rxi = QtCore.QRegExp(valid_positive_integer_regex)
        self.positive_integer_validator = QtGui.QRegExpValidator(rxi, self)

        from ATE.org.validation import valid_positive_float_1_regex
        rxf = QtCore.QRegExp(valid_positive_float_1_regex)
        positive_float_validator = QtGui.QRegExpValidator(rxf, self)

        from ATE.org.validation import valid_maskset_name_regex
        rxMaskSetName = QtCore.QRegExp(valid_maskset_name_regex)
        self.maskset_name_validator = QtGui.QRegExpValidator(rxMaskSetName, self)

    # maskset
        self.existing_masksets = self.project_info.get_maskset_names()

        self.masksetName.setText("")
        self.masksetName.setValidator(self.maskset_name_validator)

    # Type & Customer
        self.Type.setCurrentText('ASSP')
        self.customerLabel.setVisible(False)
        self.customer.setText('')
        self.customer.setVisible(False)

    # wafer diameter
        self.waferDiameter.setCurrentIndex(self.waferDiameter.findText('200'))

    # bondpads
        self.bondpads.setMinimum(2)
        self.bondpads.setMaximum(99)
        self.bondpads.setValue(2)
        self._set_row_elements(DEFAULT_ROW)

    # XY Flip Button
        self.XYFlipButton.setText("")
        self.XYFlipButton.setIcon(qta.icon('mdi.arrow-up-down', color='white'))

    # die size X
        NewMasksetWizard._setup_input_element(self.dieSizeX, "", self.positive_integer_validator)
    # die size Y
        NewMasksetWizard._setup_input_element(self.dieSizeY, "", self.positive_integer_validator)
    # die Ref X
        NewMasksetWizard._setup_input_element(self.dieRefX, "", positive_float_validator)
    # die Ref Y
        NewMasksetWizard._setup_input_element(self.dieRefY, "", positive_float_validator)
    # X Offset
        NewMasksetWizard._setup_input_element(self.xOffset, "0", positive_float_validator)
    # Y Offset
        NewMasksetWizard._setup_input_element(self.yOffset, "0", positive_float_validator)
    # scribe X
        NewMasksetWizard._setup_input_element(self.scribeX, str(standard_scribe), positive_float_validator)
    # scribe Y
        NewMasksetWizard._setup_input_element(self.scribeY, str(standard_scribe), positive_float_validator)

    # Flat
        WaferDiameter = int(self.waferDiameter.currentText())
        Flat = (WaferDiameter / 2) - standard_flat_height
        if Flat - int(Flat) == 0:
            self.flat.setText(str(int(Flat)))
        else:
            self.flat.setText(str(Flat))

    # bondpad table
        self.bondpadTable.setRowCount(self.bondpads.value())
        self.bondpadTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bondpadTable.customContextMenuRequested.connect(self._context_menu)
        self.bondpadTable.itemDoubleClicked.connect(self._double_click_handler)
        self.bondpadTable.itemClicked.connect(self._select_item)
        self.bondpadTable.itemSelectionChanged.connect(self._table_clicked)
        self.bondpadTable.itemEntered.connect(self._item_entered)

        self.pad_type = {PadType.Analog(): self.select_analog_pad_type,
                         PadType.Digital(): self.select_digital_pad_type,
                         PadType.Mixed(): self.select_mixed_pad_type,
                         PadType.Power(): self.select_power_pad_type}

        self.pad_direction = {PadDirection.Input(): self.select_input_direction,
                              PadDirection.Output(): self.select_output_direction,
                              PadDirection.Bidirectional(): self.select_bidirectional_direction}

        self.pad_standard_size = {PadStandardSize.Standard_1(): self._standard_1_selected,
                                  PadStandardSize.Standard_2(): self._standard_2_selected,
                                  PadStandardSize.Standard_3(): self._standard_3_selected}

        # resize cell columns
        for c in range(self.columns):
            if c == PAD_INFO.PAD_NAME_COLUMN():
                self.bondpadTable.setColumnWidth(c, PAD_INFO.NAME_COL_SIZE())

            elif c in (PAD_INFO.PAD_POS_X_COLUMN(),
                       PAD_INFO.PAD_POS_Y_COLUMN(),
                       PAD_INFO.PAD_SIZE_X_COLUMN(),
                       PAD_INFO.PAD_SIZE_Y_COLUMN(),
                       PAD_INFO.PAD_TYPE_COLUMN()):
                self.bondpadTable.setColumnWidth(c, PAD_INFO.REF_COL_SIZE())

            elif c == PAD_INFO.PAD_DIRECTION_COLUMN():
                self.bondpadTable.setColumnWidth(c, PAD_INFO.DIR_COL_SIZE())

        self.bondpadTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.bondpadTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

    # view die button
        self.viewDieButton.setText("")
        self.viewDieButton.setIcon(qta.icon('mdi.eye-outline', color='white'))
        self.viewDieButton.clicked.connect(self.viewDie)

    # import For
        importer_name_lists = self.plugin_manager.hook.get_importer_names()
        self.importFor.clear()
        self.importFor.addItem('')
        for importer_name_list in importer_name_lists:
            for importer_name in importer_name_list:
                self.importFor.addItem(importer_name["display_name"])
                self.plugin_names.append(importer_name)
        self.importFor.setCurrentIndex(0)  # empty string

    # feedback
        self.feedback.setText("")
        self.feedback.setStyleSheet('color: orange')

        self.validate()

    @staticmethod
    def _setup_input_element(element, text, validator):
        element.blockSignals(True)
        element.setText(text)
        element.setValidator(validator)
        element.blockSignals(False)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _item_entered(self, item):
        if item.column() in (PAD_INFO.PAD_DIRECTION_COLUMN(), PAD_INFO.PAD_TYPE_COLUMN()):
            self._update_row(item.row())

    def _set_row_elements(self, elements):
        self.bondpadTable.setRowCount(self.bondpads.value())
        num_rows = self.bondpadTable.rowCount()

        for row in range(num_rows):
            self._set_cells_content(row, elements)

    def _set_cells_content(self, row, elements):
        for column in range(self.columns):
            item = QtWidgets.QTableWidgetItem(elements[column])
            self.bondpadTable.setItem(row, column, item)

            if column == 0:
                item.setTextAlignment(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
            else:
                item.setTextAlignment(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))

    def _bondpads_changed(self, Bondpads):
        if self.rows < Bondpads:
            old_row_count = self.rows
            self.bondpadTable.setRowCount(Bondpads)
            for row in range(old_row_count, Bondpads):
                self._set_cells_content(row, DEFAULT_ROW)

            if not self.is_table_enabled:
                self._set_table_flags(QtCore.Qt.NoItemFlags)

        else:
            self.bondpadTable.removeRow(self.rows)
            self.bondpadTable.setRowCount(Bondpads)

    def _context_menu(self, point):
        if not self.is_table_enabled:
            return

        item = self.bondpadTable.itemAt(point)
        if item is None:
            return

        column = item.column()
        if column == PAD_INFO.PAD_NAME_COLUMN():
            self.create_menu(self.pad_type, self.pad_direction)
            return

        if column == PAD_INFO.PAD_TYPE_COLUMN():  # type
            self.create_menu(self.pad_type)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            return

        if column == PAD_INFO.PAD_DIRECTION_COLUMN():  # direction
            self.create_menu(self.pad_direction)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            return

        if column in (PAD_INFO.PAD_SIZE_X_COLUMN(), PAD_INFO.PAD_SIZE_Y_COLUMN()):
            self.create_menu(self.pad_standard_size)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            return

    def _set_pad_size_cells(self, value):
        for item in self.bondpadTable.selectedItems():
            row = item.row()
            for c in range(self.columns):
                if c in (PAD_INFO.PAD_SIZE_X_COLUMN(), PAD_INFO.PAD_SIZE_Y_COLUMN()):
                    self.bondpadTable.item(row, c).setText(value)

    def _standard_1_selected(self):
        self._set_pad_size_cells(PadStandardSize.Standard_1()[0])

    def _standard_2_selected(self):
        self._set_pad_size_cells(PadStandardSize.Standard_2()[0])

    def _standard_3_selected(self):
        self._set_pad_size_cells(PadStandardSize.Standard_3()[0],)

    def _double_click_handler(self, item):
        if not self.is_table_enabled:
            return

        column = item.column()
        if column == PAD_INFO.PAD_TYPE_COLUMN():
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        elif column == PAD_INFO.PAD_DIRECTION_COLUMN():
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        else:
            self._create_checkable_cell(item)

        self.selected_cell = item

    def _table_clicked(self):
        # update cell dispite no changes have been done
        if self.selected_cell is None:
            return

        self._update_row(self.selected_cell.row())
        self.selected_cell = None

    def _create_checkable_cell(self, item):
        column = item.column()
        row = item.row()
        # set cell widget to qlineEdit widget
        checkable_widget = QtWidgets.QLineEdit()
        checkable_widget.setText(item.text())

        if column == PAD_INFO.PAD_NAME_COLUMN():
            checkable_widget.setValidator(self.maskset_name_validator)
        else:
            checkable_widget.setValidator(self.positive_integer_validator)

        self.bondpadTable.setCellWidget(row, column, checkable_widget)
        checkable_widget.editingFinished.connect(lambda row=row, column=column, checkable_widget=checkable_widget:
                                                 self._edit_cell_done(checkable_widget, row, column))

    def _edit_cell_done(self, checkable_widget, row, column):
        if self.dieSizeX.text() == '' or self.dieSizeY.text() == '':
            self.feedback.setText("die size is not set yet")
            checkable_widget.clear()
            self._update_row(row)
            return

        if column == PAD_INFO.PAD_NAME_COLUMN():
            # name must be unique
            self._validate_name(checkable_widget, row, column=0)
            if not self._is_defined_only_once(column=0):
                item = self.bondpadTable.item(row, 0)
                self.feedback.setText(f'name: {item.text()} has already been used')
                item.setText('')
                self.OKButton.setEnabled(False)
                self._update_row(row)
                return

        success = True
        if column in (PAD_INFO.PAD_POS_X_COLUMN(), PAD_INFO.PAD_POS_Y_COLUMN()):
            success = self._handle_pos_cols(checkable_widget, row, column)

        elif column in (PAD_INFO.PAD_SIZE_X_COLUMN(), PAD_INFO.PAD_SIZE_Y_COLUMN()):
            success = self._validate_pads_size_references(checkable_widget, row, column)

        self._update_row(row)

        if success:
            self.feedback.setText('')
            self._validate_table(row)

    def _handle_pos_cols(self, checkable_widget, row, column):
        success = True
        if column == PAD_INFO.PAD_POS_X_COLUMN():
            success = self._validate_pads_position_references(checkable_widget, row, column, self.dieSizeX.text())
            item_x = checkable_widget.text()
            item_y = self.bondpadTable.item(row, PAD_INFO.PAD_POS_Y_COLUMN()).text()

        if column == PAD_INFO.PAD_POS_Y_COLUMN():
            success = self._validate_pads_position_references(checkable_widget, row, column, self.dieSizeY.text())
            item_x = self.bondpadTable.item(row, PAD_INFO.PAD_POS_X_COLUMN()).text()
            item_y = checkable_widget.text()

        if success:
            success = self._are_coordinates_valid(item_x, item_y, row, column)

        if not success:
            checkable_widget.clear()

        return success

    def _are_coordinates_valid(self, item_x, item_y, current_row, current_col):
        for row in range(self.rows):
            if current_row == row:
                continue
            if self.bondpadTable.item(row, PAD_INFO.PAD_POS_X_COLUMN()).text() == item_x and \
               self.bondpadTable.item(row, PAD_INFO.PAD_POS_Y_COLUMN()).text() == item_y:
                self.bondpadTable.item(current_row, current_col).setText('')
                self.feedback.setText("coordinates are already occupied")
                return False

        return True

    def _update_row(self, row):
        elements = []
        num_cols = self.bondpadTable.columnCount()
        for i in range(num_cols):
            elements.append(self.bondpadTable.item(row, i).text())

        self.bondpadTable.removeRow(row)
        self.bondpadTable.insertRow(row)
        self._set_cells_content(row, elements)

    def _validate_table(self, row=0):
        # check if all cells are filled
        for r in range(self.rows):
            for c in range(self.columns):
                item = self.table_item(r, c)
                if item.text() == '':
                    self.OKButton.setEnabled(False)
                    return

        self.OKButton.setEnabled(True)

    def _select_item(self, item):
        if not self.is_table_enabled:
            return
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
 
    @property
    def rows(self):
        return self.bondpadTable.rowCount()

    @property
    def columns(self):
        return self.bondpadTable.columnCount()

    def table_item(self, row, column):
        return self.bondpadTable.item(row, column)

    def _is_defined_only_once(self, column):
        pos_list = []
        for r in range(self.rows):
            pos_list.append(self.table_item(r, column).text())

        available_items = [x for x in pos_list if x]

        return len(set(available_items)) == len(available_items)

    def _validate_name(self, checkable_widget, row, column=0):
        self.bondpadTable.item(row, column).setText(str(checkable_widget.text()))

    def _validate_pads_size_references(self, checkable_widget, row, column):
        self.bondpadTable.item(row, column).setText(str(checkable_widget.text()))
        return True

    def _validate_pads_position_references(self, checkable_widget, row, column, die_size):
        pad_size = self.bondpadTable.item(row, column + 2).text()
        if pad_size is None:
            self.feedback.setText("pad size is not defined")
            return False

        if checkable_widget.text() == '':
            self.feedback.setText("no input value")
            return False

        pad_pos = int(checkable_widget.text())
        pad_size = int(pad_size) / 2
        die_size = int(die_size)
        if not pad_pos + pad_size < die_size:
            self.feedback.setText(f"rule (pos + size < diesize) does not hold -> ({pad_pos} + {pad_size} < {die_size})")
            return False

        self.bondpadTable.item(row, column).setText(str(pad_pos))

        return True

    def create_menu(self, *components):
        menu = QtWidgets.QMenu(self)
        for index, component in enumerate(components):
            if index > 0:
                menu.addSeparator()

            for pd, func in component.items():
                item = menu.addAction(pd[1])
                item.triggered.connect(func)

        menu.exec_(QtGui.QCursor.pos())

    def set_pad_selection(self, pad_type, column):
        for item in [item for item in self.bondpadTable.selectedItems() if item.column() == column]:
            item.setText(pad_type[0])

        # special case: user friendly option to change Type and Direction directly from name column
        for item in [item for item in self.bondpadTable.selectedItems() if item.column() == PAD_INFO.PAD_NAME_COLUMN()]:
            self.bondpadTable.item(item.row(), column).setText(pad_type[0])

    def select_input_direction(self):
        self.set_pad_selection(PadDirection.Input(), PAD_INFO.PAD_DIRECTION_COLUMN())

    def select_output_direction(self):
        self.set_pad_selection(PadDirection.Output(), PAD_INFO.PAD_DIRECTION_COLUMN())

    def select_bidirectional_direction(self):
        self.set_pad_selection(PadDirection.Bidirectional(), PAD_INFO.PAD_DIRECTION_COLUMN())

    def select_analog_pad_type(self):
        self.set_pad_selection(PadType.Analog(), PAD_INFO.PAD_TYPE_COLUMN())

    def select_digital_pad_type(self):
        self.set_pad_selection(PadType.Digital(), PAD_INFO.PAD_TYPE_COLUMN())

    def select_mixed_pad_type(self):
        self.set_pad_selection(PadType.Mixed(), PAD_INFO.PAD_TYPE_COLUMN())

    def select_power_pad_type(self):
        self.set_pad_selection(PadType.Power(), PAD_INFO.PAD_TYPE_COLUMN())

    def _connect_event_handler(self):
        self.masksetName.textChanged.connect(self.nameChanged)

        self.Type.currentTextChanged.connect(self.typeChanged)
        self.customer.textChanged.connect(self.customerChanged)

        self.waferDiameter.currentTextChanged.connect(self.waferDiameterChanged)
        self.bondpads.valueChanged.connect(self._bondpads_changed)
        self.dieSizeX.textChanged.connect(self._die_size_x_changed)

        self.XYFlipButton.clicked.connect(self.xy_flip)

        self.dieSizeY.textChanged.connect(self._die_size_y_changed)
        self.dieRefX.textChanged.connect(self.dieRefXChanged)
        self.dieRefY.textChanged.connect(self.dieRefYChanged)
        self.xOffset.textChanged.connect(self.xOffsetChanged)
        self.scribeX.textChanged.connect(self.scribeXChanged)
        self.yOffset.textChanged.connect(self.yOffsetChanged)
        self.scribeY.textChanged.connect(self.scribeYChanged)
    # Wafer Map Editor
        self.editWaferMapButton.clicked.connect(self.editWaferMap)

        self.importFor.currentTextChanged.connect(self.importForChanged)
    # buttons
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)

    def nameChanged(self, MaskSetName):
        self.validate(MaskSetName)

    def typeChanged(self, SelectedType):
        if SelectedType == 'ASSP':
            self.customerLabel.setVisible(False)
            self.customer.blockSignals(True)
            self.customer.setText('')
            self.customer.setVisible(False)
            self.customer.blockSignals(False)
        else:  # 'ASIC'
            self.customerLabel.setVisible(True)
            self.customer.blockSignals(True)
            self.customer.setText('')
            self.customer.setVisible(True)
            self.customer.blockSignals(False)

        self.validate()

    def customerChanged(self, Customer):
        self.validate()

    def waferDiameterChanged(self, WaferDiameter):
        WaferDiameter = int(WaferDiameter)
        Flat = (WaferDiameter / 2) - standard_flat_height
        if (Flat - int(Flat)) == 0:
            self.flat.setText(str(int(Flat)))
        else:
            self.flat.setText(str(Flat))

        self.validate()

    def _die_size_changed(self, die_size, die_ref):
        if die_size != '':
            die_size = int(die_size)
            mid = int(die_size) / 2
            if mid - int(mid) == 0:
                die_ref.setText(str(int(mid)))
            else:
                die_ref.setText(str(mid))
        else:
            die_ref.setText('')

        self.validate()

    def _die_size_x_changed(self, die_size_x):
        self._die_size_changed(die_size_x, self.dieRefX)

    def _die_size_y_changed(self, die_size_y):
        self._die_size_changed(die_size_y, self.dieRefY)

    def xy_flip(self):
        old_die_size_x = self.dieSizeX.text()
        old_die_size_y = self.dieSizeY.text()
        old_die_ref_x = self.dieRefX.text()
        old_die_ref_y = self.dieRefY.text()

        self.dieSizeX.setText(old_die_size_y)
        self.dieSizeY.setText(old_die_size_x)
        self.dieRefX.setText(old_die_ref_y)
        self.dieRefY.setText(old_die_ref_x)

        # self.validate() # ?!?

    def dieRefXChanged(self, DieRefX):
        pass

    def dieRefYChanged(self, DieRefY):
        pass

    def xOffsetChanged(self, XOffset):
        pass

    def yOffsetChanged(self, YOffset):
        pass

    def scribeXChanged(self, ScribeX):
        pass

    def scribeYChanged(self, ScribeY):
        pass

    def importForChanged(self, Company):
        if Company == '':
            self.OKButton.setText("OK")
            self.validate()
        else:
            self.OKButton.setText("Import")
            self.OKButton.setEnabled(True)
            self.feedback.setText(f"About to import a Maskset from using the {self.importFor.currentText()} plugin")

    def validateTable(self):
        '''
        this method returns an 'error string' (that can be copied into the feedback line)
        if everything is ok, an empty string is returned.
        '''
        retval = ''
        # TODO: Implement the validation of the table
        return retval

    def validate(self, MaskSetName=''):
        self.feedback.setText('')
        # MasksetName
        if MaskSetName == '':
            MaskSetName = self.masksetName.text()
        if MaskSetName == '':
            self.feedback.setText("Supply a MaskSet name")
        else:
            if not self.read_only and MaskSetName in self.existing_masksets:
                self.feedback.setText("MaskSet name already defined")
            if not is_valid_maskset_name(MaskSetName):
                self.feedback.setText("Invalid MaskSet name")
        # DieSizeX
        if self.feedback.text() == '':
            if self.dieSizeX.text() == '':
                self.feedback.setText("Supply a Die Size X value")

        # DieSizeY
        if self.feedback.text() == '':
            if self.dieSizeY.text() == '':
                self.feedback.setText("Supply a Die Size Y value")

        # DieRefX
        if self.feedback.text() == '':
            if self.dieRefX.text() == '':
                self.feedback.setText("Supply a Die Ref X value")

        # DieRefY
        if self.feedback.text() == '':
            if self.dieRefY.text() == '':
                self.feedback.setText("Supply a Die Ref Y value")

        # XOffset
        if self.feedback.text() == '':
            if self.xOffset.text() == '':
                self.feedback.setText("Supply an X Offset value")

        # YOffset
        if self.feedback.text() == '':
            if self.yOffset.text() == '':
                self.feedback.setText("Supply an Y Offset value")

        # ScribeX
        if self.feedback.text() == '':
            if self.scribeX.text() == '':
                self.feedback.setText("Supply a Scribe Size X value")

        # ScribeY
        if self.feedback.text() == '':
            if self.scribeY.text() == '':
                self.feedback.setText("Supply a Scribe Size Y value")

        # Flat
        if self.feedback.text() == '':
            if self.flat.text() == '':
                self.feedback.setText("Supply a Flat distance value")

        if not self.feedback.text() == '':
            self.OKButton.setEnabled(False)
            self._set_table_flags(QtCore.Qt.NoItemFlags)
            self.is_table_enabled = False
            return

        # enable table
        self._set_table_flags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.is_table_enabled = True
        self._validate_table()

    def _set_table_flags(self, flags):
        for r in range(self.rows):
            for c in range(self.columns):
                item = self.bondpadTable.item(r, c)
                item.setFlags(flags)

    def editWaferMap(self):
        print("Wafer Map Editor not yet implemented")
        # TODO: add the wafer map editor here

    def viewDie(self):
        print("Die Viewer not yet implemented")
        # TODO: add the die viewer (based ont the table here)

    def serialize_table_data(self):
        table_infos = {}
        for r in range(self.rows):
            data = ()
            for c in range(self.columns):
                item = self.bondpadTable.item(r, c)
                cell_data = item.text()
                if c in range(1, 5):
                    cell_data = int(item.text())
                data += (cell_data,)

            table_infos[r + 1] = data

        return table_infos

    def _get_maskset_definition(self):
        return {'WaferDiameter': int(self.waferDiameter.currentText()),
                'Bondpads': self.bondpads.value(),
                'DieSize': (int(self.dieSizeX.text()), int(self.dieSizeY.text())),
                'DieRef': (float(self.dieRefX.text()), float(self.dieRefY.text())),
                'Offset': (int(self.xOffset.text()), int(self.yOffset.text())),
                'Scribe': (float(self.scribeX.text()), float(self.scribeY.text())),
                'Flat': float(self.flat.text()),
                'BondpadTable': self.serialize_table_data(),

                # TODO: future impl.
                'Wafermap': {'rim': [(100, 80), (-80, -100)],  # list of x- and y- coordinates of dies that are not to be tested (belong to rim)
                             'blank': [(80, 80)],  # list of x- and y- coordinates of dies that don't exist (blank silicon)
                             'test_insert': [],  # list of x- and y- coodinates of dies that don't exist (test inserts)
                             'unused': []  # list of x- and y- coordinates of dies taht are not used (probing optimization ?)
                             }  # implement wafermap
                }

    def OKButtonPressed(self):
        if self.OKButton.text() == "Import":
            if self.importFor.currentIndex() < 1:
                return

            # nasty to do this text based, but here we go.
            importerIndex = self.importFor.currentIndex() - 1

            if len(self.plugin_names) <= importerIndex:
                return

            importerName = self.plugin_names[importerIndex]
            importer = self.plugin_manager.hook.get_importer(importer_name=importerName["name"])

            if len(importer) != 1:
                self.feedback.setText("Failed to load importer. The respective plugin failed to provide exactly one instance.")
                return

            result = importer[0].do_import()
            if not result:
                self.feedback.setText(f"Failed to import, reason: {importer[0].get_abort_reason()}")
            else:
                self.importFor.setCurrentIndex(0)
                self.OKButton.setText("OK")
                self.validate()
        else:
            name = self.masksetName.text()
            if self.Type.currentText() == 'ASSP':
                customer = ''
            else:  # 'ASIC' so need a customer !
                customer = self.customer.text()
            self.project_info.add_maskset(name, customer, self._get_maskset_definition())
            self.accept()

    def CancelButtonPressed(self):
        self.reject()


def new_maskset_dialog(parent):
    newMasksetWizard = NewMasksetWizard(parent)
    newMasksetWizard.exec_()
    del(newMasksetWizard)
