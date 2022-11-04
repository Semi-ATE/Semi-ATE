import numpy as np

from enum import Enum, unique
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import keyword
from ate_common.parameter import InputColumnKey, InputColumnLabel, OutputColumnKey, OutputColumnLabel


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


@unique
class InputColumnIndex(Enum):
    SHMOO = 0
    NAME = 1
    MIN = 2
    DEFAULT = 3
    MAX = 4
    POWER = 5
    UNIT = 6
    FMT = 7

    def __call__(self):
        return self.value


@unique
class OutputColumnIndex(Enum):
    NAME = 0
    LSL = 1
    LTL = 2
    NOM = 3
    UTL = 4
    USL = 5
    POWER = 6
    UNIT = 7
    MPR = 8
    FMT = 9

    def __call__(self):
        return self.value


OUTPUT_MAX_NUM_COLUMNS = max([e.value for e in OutputColumnIndex]) + 1
INPUT_MAX_NUM_COLUMNS = max([e.value for e in InputColumnIndex]) + 1

OUTPUT_PARAMETER_COLUMN_MAP = [
    {'type': OutputColumnIndex.NAME,  'key': OutputColumnKey.NAME(),  'label': OutputColumnLabel.NAME(),  'default': 'parameterX_name'},
    {'type': OutputColumnIndex.LSL,   'key': OutputColumnKey.LSL(),   'label': OutputColumnLabel.LSL(),   'default': -np.inf},
    {'type': OutputColumnIndex.LTL,   'key': OutputColumnKey.LTL(),   'label': OutputColumnLabel.LTL(),   'default': np.nan},
    {'type': OutputColumnIndex.NOM,   'key': OutputColumnKey.NOM(),   'label': OutputColumnLabel.NOM(),   'default': 0.0},
    {'type': OutputColumnIndex.UTL,   'key': OutputColumnKey.UTL(),   'label': OutputColumnLabel.UTL(),   'default': np.nan},
    {'type': OutputColumnIndex.USL,   'key': OutputColumnKey.USL(),   'label': OutputColumnLabel.USL(),   'default': np.inf},
    {'type': OutputColumnIndex.POWER, 'key': OutputColumnKey.POWER(), 'label': OutputColumnLabel.POWER(), 'default': '˽'},
    {'type': OutputColumnIndex.UNIT,  'key': OutputColumnKey.UNIT(),  'label': OutputColumnLabel.UNIT(),  'default': '˽'},
    {'type': OutputColumnIndex.FMT,   'key': OutputColumnKey.FMT(),   'label': OutputColumnLabel.FMT(),   'default': '.3f'},
    {'type': OutputColumnIndex.MPR,   'key': OutputColumnKey.MPR(),   'label': OutputColumnLabel.MPR(),   'default': False},
]

INPUT_PARAMETER_COLUMN_MAP = [
    {'type': InputColumnIndex.SHMOO,   'key': InputColumnKey.SHMOO(),   'label': InputColumnLabel.SHMOO(),   'default': None},
    {'type': InputColumnIndex.NAME,    'key': InputColumnKey.NAME(),    'label': InputColumnLabel.NAME(),    'default': 'parameterX_name'},
    {'type': InputColumnIndex.MIN,     'key': InputColumnKey.MIN(),     'label': InputColumnLabel.MIN(),     'default': None},
    {'type': InputColumnIndex.DEFAULT, 'key': InputColumnKey.DEFAULT(), 'label': InputColumnLabel.DEFAULT(), 'default': None},
    {'type': InputColumnIndex.MAX,     'key': InputColumnKey.MAX(),     'label': InputColumnLabel.MAX(),     'default': None},
    {'type': InputColumnIndex.POWER,   'key': InputColumnKey.POWER(),   'label': InputColumnLabel.POWER(),   'default': '˽'},
    {'type': InputColumnIndex.UNIT,    'key': InputColumnKey.UNIT(),    'label': InputColumnLabel.UNIT(),    'default': '˽'},
    {'type': InputColumnIndex.FMT,     'key': InputColumnKey.FMT(),     'label': InputColumnLabel.FMT(),     'default': None},
]


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


class NameDelegator(Delegator):
    """Custom Delegator Class for 'Name'.

    It works with regex AND verifies that the name doesn't exist
    """

    def __init__(self, regex, existing_names, parent=None):
        self.super().__init__(regex, parent)
        self.existing_names = existing_names
        self.commitData.commitData.connect(self.validate_name)

    def validate_name(self, editor):
        """Make sure the entered name does not exist already."""
        # TODO: implement, e.q use valid_name_regex
        if editor.text() in self.existing_names:
            pass


def make_blank_definition(project_info):
    '''
    this function creates a blank definition dictionary with 'hardware', 'base' and Type
    '''
    retval = {}
    retval['name'] = ''
    retval['type'] = ''
    retval['hardware'] = project_info.active_hardware
    retval['base'] = project_info.active_base
    retval['docstring'] = []
    retval['input_parameters'] = {'Temperature': make_default_input_parameter(temperature=True)}
    retval['output_parameters'] = {'new_parameter1': make_default_output_parameter()}
    retval['dependencies'] = {}
    retval['patterns'] = []
    return retval


def make_default_input_parameter(temperature: bool = False):
    input_parameters_without_name = list(filter(lambda e: e['type'] != InputColumnIndex.NAME, INPUT_PARAMETER_COLUMN_MAP))
    input_key_list = list(map(lambda e: e['key'], input_parameters_without_name))
    input_default_list = list(map(lambda e: e['default'], input_parameters_without_name))
    default_input_parameter = dict(zip(input_key_list, input_default_list))
    if temperature is True:
        default_input_parameter[InputColumnKey.SHMOO()] = True
        default_input_parameter[InputColumnKey.MIN()] = -40
        default_input_parameter[InputColumnKey.DEFAULT()] = 25
        default_input_parameter[InputColumnKey.MAX()] = 170
        default_input_parameter[InputColumnKey.UNIT()] = '°C'
        default_input_parameter[InputColumnKey.FMT()] = '.0f'
    return default_input_parameter


def make_default_output_parameter(empty: bool = False):
    output_parameters_without_name = list(filter(lambda e: e['type'] != OutputColumnIndex.NAME, OUTPUT_PARAMETER_COLUMN_MAP))
    output_key_list = list(map(lambda e: e['key'], output_parameters_without_name))
    output_default_list = list(map(lambda e: e['default'], output_parameters_without_name))
    default_output_parameter = dict(zip(output_key_list, output_default_list))
    if empty is True:
        default_output_parameter[OutputColumnKey.LSL()] = None
        default_output_parameter[OutputColumnKey.LTL()] = None
        default_output_parameter[OutputColumnKey.NOM()] = None
        default_output_parameter[OutputColumnKey.UTL()] = None
        default_output_parameter[OutputColumnKey.USL()] = None
        default_output_parameter[OutputColumnKey.POWER()] = '˽'
        default_output_parameter[OutputColumnKey.UNIT()] = '˽'
        default_output_parameter[OutputColumnKey.FMT()] = ''
        default_output_parameter[OutputColumnKey.MPR()] = False
    return default_output_parameter
