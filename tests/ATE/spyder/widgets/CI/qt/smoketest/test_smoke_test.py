from ATE.spyder.widgets.navigation import ProjectNavigation
from ATE.spyder.widgets.actions_on.model.TreeModel import TreeModel
from ATE.spyder.widgets.actions_on.project.ProjectWizard import ProjectWizard
from ATE.spyder.widgets.actions_on.hardwaresetup.HardwareWizard import HardwareWizard
from ATE.spyder.widgets.actions_on.maskset.NewMasksetWizard import NewMasksetWizard
from ATE.spyder.widgets.actions_on.die.DieWizard import DieWizard
from ATE.spyder.widgets.actions_on.package.NewPackageWizard import NewPackageWizard
from ATE.spyder.widgets.actions_on.device.NewDeviceWizard import NewDeviceWizard
from ATE.spyder.widgets.actions_on.product.NewProductWizard import NewProductWizard
from ATE.spyder.widgets.actions_on.flow.HTOL.htolwizard import HTOLWizard
from ATE.spyder.widgets.actions_on.tests.TestWizard import TestWizard
from ATE.spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard
from ATE.spyder.widgets.actions_on.program.EditTestProgramWizard import EditTestProgramWizard
from ATE.projectdatabase.FileOperator import FileOperator

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QMainWindow

import os
import shutil
import pytest
import json
from pytestqt.qt_compat import qt_api
from PyQt5 import QtCore, QtWidgets


bin_table = {
    '1': [0, 1],
    '2': [10],
    '3': [11],
}

PROJECT_NAME = 'smoke_test'
SETTING_QUALITY_GRADE = "Commercial"


def generate_bin_table():
    path = os.path.join(os.path.dirname(__file__), PROJECT_NAME, 'src', test_configruation['hardware'], test_configruation['base'])
    with open(os.path.join(path, 'binmapping.json'), 'w+') as f:
        json.dump(bin_table, f)


class MockDBObject:
    def __init__(self, definition):
        self.__definition = definition

    def get_definition(self):
        return self.__definition


class MockATEWidgets(QMainWindow):
    # dummy Signals
    sig_edit_goto_requested = Signal(str, int, str)

    database_changed = Signal(int)
    toolbar_changed = Signal(str, str, str)
    active_project_changed = Signal()
    hardware_added = Signal(str)
    hardware_activated = Signal(str)
    hardware_removed = Signal(str)
    update_target = Signal()
    select_target = Signal(str)
    select_base = Signal(str)
    select_hardware = Signal(str)
    update_settings = Signal(str, str, str)
    test_target_deleted = Signal(str, str)
    group_state_changed = Signal()
    group_added = Signal(str)
    group_removed = Signal(str)
    groups_update = Signal(str, list)

    def __init__(self):
        super().__init__()


definitions = {'hardware': 'HW0',
               'maskset': 'Mask1',
               'die': 'Die1',
               'package': 'Package1',
               'device': 'Device1',
               'product': 'Product1',
               'test': 'DBC',
               'test1': 'CBA',
               'test2': 'EFG'}


test_configruation = {'name': definitions['test'],
# TODO: edit wizard is planned for future extension to cover more cases
                      'hardware': definitions['hardware'],
                      'type': 'custom',
                      'base': 'PR',
                      'owner': 'Production_PR',
                      'prog_name': 'smoke_test_HW0_PR_Die1_Production_PR_1',
                      'input_parameters': {'T': {'name': 'foo', 'Min': -40, 'Max': 170, 'Default': 25, 'Unit': '°C', 'fmt': '.3f', '10ᵡ': '1', 'Shmoo': 'False'}},
                      'output_parameters': {'parameter2_name': {'name': 'foo', 'LSL': 100, 'USL': -100, 'LTL': 0, 'UTL': 0, 'Nom': 2.5, 'Unit': 'mV', 'fmt': '.3f', '10ᵡ': '1'}},
                      'docstring': 'test DBC'
                      }


def debug_message(message):
    qt_api.qWarning(message)


# using this function when running CI build will block for ever
# !!! DON'T !!!
# just for localy debuging purposes
def debug_visual(window, qtbot):
    window.show()
    qtbot.stopForInteraction()


main = None


def mainwindow():
    global main
    return MockATEWidgets() if main is None else main


@pytest.fixture(scope='module')
def project_navigation():
    root_name = os.path.dirname(__file__)
    dir_name = os.path.join(root_name, PROJECT_NAME)
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    main_window = mainwindow()
    with ProjectNavigation(dir_name, root_name, main_window) as project_info:
        yield project_info


@pytest.fixture(scope='module')
def model(project_navigation):
    main_window = mainwindow()
    with TreeModel(project_navigation, parent=main_window) as model:
        yield model


@pytest.fixture
def project(qtbot, project_navigation):
    dialog = ProjectWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_project_cancel_before_enter_name(project, qtbot):
    qtbot.mouseClick(project.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_project_ok(project, qtbot):
    project.qualityGrade.setCurrentText(SETTING_QUALITY_GRADE)
    qtbot.mouseClick(project.OKButton, QtCore.Qt.LeftButton)


def test_check_settings_quality_grade(project_navigation):
    assert project_navigation.get_default_quality_grade() == SETTING_QUALITY_GRADE


@pytest.fixture
def hardware(qtbot, mocker, project_navigation):
    dialog = HardwareWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_hardware_cancel_before_enter_name(hardware, qtbot):
    qtbot.mouseClick(hardware.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_hardware_enter_name(hardware, qtbot):
    hardware.hardware.clear()
    hardware.hardware.setEnabled(True)
    qtbot.keyClicks(hardware.hardware, definitions['hardware'])
    qtbot.keyClicks(hardware.singlesiteLoadboard, 'abc')
    qtbot.mouseClick(hardware.OKButton, QtCore.Qt.LeftButton)


def test_add_actuator_to_pr(hardware, qtbot):
    hardware.hardware.clear()
    hardware.hardware.setEnabled(True)
    qtbot.keyClicks(hardware.hardware, 'HW1')
    qtbot.keyClicks(hardware.singlesiteLoadboard, 'abc')
    for row in range(0, hardware.usedActuators.rowCount()):
        hardware.usedActuators.item(row, 1).setCheckState(0)
        hardware.usedActuators.item(row, 2).setCheckState(0)
    qtbot.mouseClick(hardware.OKButton, QtCore.Qt.LeftButton)
    hardware.usedActuators.item(1, 1).setCheckState(2)


def test_add_actuator_to_ft(hardware, qtbot):
    hardware.hardware.clear()
    hardware.hardware.setEnabled(True)
    qtbot.keyClicks(hardware.hardware, 'HW2')
    qtbot.keyClicks(hardware.singlesiteLoadboard, 'abc')
    for row in range(0, hardware.usedActuators.rowCount()):
        hardware.usedActuators.item(row, 1).setCheckState(0)
        hardware.usedActuators.item(row, 2).setCheckState(0)
    qtbot.mouseClick(hardware.OKButton, QtCore.Qt.LeftButton)
    hardware.usedActuators.item(1, 2).setCheckState(2)


@pytest.fixture
def maskset(qtbot, mocker, project_navigation):
    dialog = NewMasksetWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_masket_cancel_before_enter_name(maskset, qtbot):
    qtbot.mouseClick(maskset.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_maskset_enter_name(maskset, qtbot):
    qtbot.keyClicks(maskset.masksetName, definitions['maskset'])
    qtbot.keyClicks(maskset.dieSizeX, '1000')
    qtbot.keyClicks(maskset.dieSizeY, '1000')
    for row in range(maskset.bondpadTable.rowCount()):
        for c in range(maskset.bondpadTable.columnCount()):
            if c == 0:
                maskset.bondpadTable.item(row, c).setText(f"{row}")
            if c in (1, 2):
                maskset.bondpadTable.item(row, c).setText(f"{c}")

    maskset.OKButton.setEnabled(True)

    qtbot.mouseClick(maskset.OKButton, QtCore.Qt.LeftButton)


@pytest.fixture
def die(qtbot, mocker, project_navigation):
    dialog = DieWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_die_cancel_before_enter_name(die, qtbot):
    qtbot.mouseClick(die.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_die_enter_name(die, qtbot):
    qtbot.keyClicks(die.dieName, definitions['die'])
    qtbot.mouseClick(die.OKButton, QtCore.Qt.LeftButton)


@pytest.fixture
def package(qtbot, mocker, project_navigation):
    dialog = NewPackageWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_package_cancel_before_enter_name(package, qtbot):
    qtbot.mouseClick(package.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_package_enter_name(package, qtbot):
    qtbot.keyClicks(package.packageName, definitions['package'])
    qtbot.mouseClick(package.OKButton, QtCore.Qt.LeftButton)


@pytest.fixture
def device(qtbot, mocker, project_navigation):
    dialog = NewDeviceWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_device_cancel_before_enter_name(device, qtbot):
    qtbot.mouseClick(device.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_device_enter_name(device, qtbot):
    qtbot.keyClicks(device.deviceName, definitions['device'])
    device.diesInDevice.insertItem(device.diesInDevice.count(), device.available_dies[0])
    device.OKButton.setEnabled(True)
    qtbot.mouseClick(device.OKButton, QtCore.Qt.LeftButton)


@pytest.fixture
def product(qtbot, mocker, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    dialog = NewProductWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_product_cancel_before_enter_name(product, qtbot):
    qtbot.mouseClick(product.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_product_enter_name(product, qtbot):
    qtbot.keyClicks(product.ProductName, definitions['product'])
    qtbot.mouseClick(product.OKButton, QtCore.Qt.LeftButton)


@pytest.fixture
def flow(qtbot, mocker, project_navigation):
    dialog = HTOLWizard(FileOperator._make_db_object({"product": definitions['product']}), project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_flow_cancel_before_enter_name(flow, qtbot):
    cancelButton = flow.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
    qtbot.mouseClick(cancelButton, QtCore.Qt.LeftButton)


def test_create_new_flow_enter_name(flow, qtbot):
    txt = flow.grpParams.findChild(QtWidgets.QLineEdit, 'txtname')
    qtbot.keyClicks(txt, 'abc')
    OKButton = flow.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    qtbot.mouseClick(OKButton, QtCore.Qt.LeftButton)


# check if data stored correctly inside the database
def test_db_data(project_navigation):
    assert project_navigation.get_hardware_state(definitions['hardware'])
    assert project_navigation.get_maskset_state(definitions['maskset'])
    assert project_navigation.get_die_state(definitions['die'])
    assert project_navigation.get_package_state(definitions['package'])
    assert project_navigation.get_device_state(definitions['device'])
    assert project_navigation.get_product_state(definitions['product'])
    assert len(project_navigation.get_data_for_qualification_flow('qualification_HTOL_flow', definitions['product']))


def test_changed_hardware_state(model):
    assert model.project_info.get_hardware_state(definitions['hardware'])
    model.hardwaresetup.get_child(definitions['hardware'])._set_state(False)

    assert not model.project_info.get_hardware_state(definitions['hardware'])
    assert not model.project_info.get_die_state(definitions['die'])
    assert not model.project_info.get_device_state(definitions['device'])
    assert not model.project_info.get_product_state(definitions['product'])
    assert model.project_info.get_maskset_state(definitions['maskset'])
    assert model.project_info.get_package_state(definitions['package'])
    # enable hw
    model.hardwaresetup.get_child(definitions['hardware'])._set_state(True)


# without using this hack, observer will prevent shutill to clean up
class FakeObserver:
    def __init__(self):
        pass


def test_update_toolbar_parameter_not_base_and_target(model):
    model.apply_toolbar_change(definitions['hardware'], '', '')
    assert model.tests_section._is_hidden
    assert model.flows._is_hidden


def test_update_toolbar_parameters_with_base_and_target(qtbot, model, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    project_navigation.active_target = definitions['device']
    model.apply_toolbar_change(definitions['hardware'], 'PR', definitions['device'])
    assert not model.tests_section._is_hidden
    assert not model.flows._is_hidden


@pytest.fixture
def new_test(qtbot, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    dialog = TestWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_test_cancel_before_enter_name(new_test, qtbot):
    qtbot.mouseClick(new_test.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_test_enter_name(new_test, qtbot):
    new_test.group_combo.model().item(0, 0).setCheckState(QtCore.Qt.Checked)
    with qtbot.waitSignal(new_test.TestName.textChanged, timeout=500):
        qtbot.keyClicks(new_test.TestName, definitions['test'])
    qtbot.mouseClick(new_test.OKButton, QtCore.Qt.LeftButton)


def test_create_and_edit_test(project_navigation, qtbot):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    new_test = TestWizard(project_navigation)
    qtbot.addWidget(new_test)
    new_test.group_combo.model().item(0, 0).setCheckState(QtCore.Qt.Checked)
    with qtbot.waitSignal(new_test.TestName.textChanged, timeout=500):
        qtbot.keyClicks(new_test.TestName, definitions['test2'])

    qtbot.mouseClick(new_test.OKButton, QtCore.Qt.LeftButton)

    the_test = project_navigation.get_test(definitions['test2'], definitions['hardware'], 'PR')
    edit_wizard = TestWizard(project_navigation, the_test.definition, True)
    # Add an output parameter
    edit_wizard.testTabs.currentIndex = 2
    qtbot.mouseClick(edit_wizard.outputParameterAdd, QtCore.Qt.LeftButton)
    qtbot.mouseClick(edit_wizard.OKButton, QtCore.Qt.LeftButton)
    # Add an input parameter
    edit_wizard.testTabs.currentIndex = 1
    qtbot.mouseClick(edit_wizard.inputParameterAdd, QtCore.Qt.LeftButton)
    qtbot.mouseClick(edit_wizard.OKButton, QtCore.Qt.LeftButton)
    the_test = project_navigation.get_test(definitions['test2'], definitions['hardware'], 'PR')
    assert(2 == len(the_test.definition["input_parameters"]))
    assert(2 == len(the_test.definition["output_parameters"]))


def test_does_test_exist(project_navigation):
    assert project_navigation.get_test(definitions['test'], definitions['hardware'], 'PR')


@pytest.fixture
def new_test_program(mocker, qtbot, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    project_navigation.active_target = definitions['device']
    from qtpy.QtGui import QStandardItem
    parent = QStandardItem('production')
    mocker.patch.object(ProjectNavigation, 'get_devices_for_hardwares', return_value=[definitions['device']])
    dialog = TestProgramWizard(project_navigation, test_configruation['owner'], parent)
    return dialog


def test_create_new_test_program_cancel_before_enter_name(new_test_program, qtbot):
    qtbot.mouseClick(new_test_program.CancelButton, QtCore.Qt.LeftButton)


def test_create_new_test_program_enter_name(new_test_program: TestProgramWizard, qtbot):
    new_test_program._verify()
    # hack: we cannot simulate combo box selection
    new_test_program.availableTests.addItem(definitions['test'])
    new_test_program.availableTests.item(0).setSelected(True)
    qtbot.mouseClick(new_test_program.testAdd, QtCore.Qt.LeftButton)
    qtbot.mouseClick(new_test_program.testAdd, QtCore.Qt.LeftButton)
    new_test_program.availableTests.item(0).setSelected(False)
    iterator = QtWidgets.QTreeWidgetItemIterator(new_test_program.binning_tree, QtWidgets.QTreeWidgetItemIterator.NoChildren)
    while iterator.value():
        item = iterator.value()

        item.setText(1, 'bin_1')

        iterator += 1

    new_test_program.user_name.setText('TheTest')
    new_test_program.binning_table.setRowCount(1)
    sb_name = QtWidgets.QTableWidgetItem()
    sb_name.setText('bin_1')
    new_test_program.binning_table.setItem(0, 0, sb_name)
    sb_num = QtWidgets.QTableWidgetItem()
    sb_num.setText('1')
    new_test_program.binning_table.setItem(0, 1, sb_num)
    sb_group = QtWidgets.QTableWidgetItem()
    sb_group.setText('abc')
    new_test_program.binning_table.setItem(0, 2, sb_group)
    sb_desc = QtWidgets.QTableWidgetItem()
    sb_desc.setText('')
    new_test_program.binning_table.setItem(0, 3, sb_desc)

    generate_bin_table()
    new_test_program._verify()

    qtbot.mouseClick(new_test_program.OKButton, QtCore.Qt.LeftButton)


def test_does_test_program_exist(project_navigation):
    assert project_navigation.get_programs_for_hardware(definitions['hardware'])


def test_does_test_target_exist(project_navigation):
    assert len(project_navigation.get_available_test_targets(test_configruation['hardware'], test_configruation['base'], definitions['test']))


@pytest.fixture
def edit_test_program(qtbot, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    project_navigation.active_target = definitions['device']
    project_navigation.user_name = definitions['usertext']
    dialog = EditTestProgramWizard(test_configruation['prog_name'], project_navigation, "HW0_PR_Die1_Production_PR")
    qtbot.addWidget(dialog)
    return dialog
