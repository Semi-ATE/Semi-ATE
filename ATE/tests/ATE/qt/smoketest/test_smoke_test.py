from ATE.org.navigation import ProjectNavigation
from ATE.org.toolbar import ToolBar
from ATE.org.actions_on.model.TreeModel import TreeModel

from ATE.org.actions_on.project.ProjectWizard import ProjectWizard
from ATE.org.actions_on.hardwaresetup.HardwareWizard import HardwareWizard
from ATE.org.actions_on.maskset.NewMasksetWizard import NewMasksetWizard
from ATE.org.actions_on.die.DieWizard import DieWizard
from ATE.org.actions_on.package.NewPackageWizard import NewPackageWizard
from ATE.org.actions_on.device.NewDeviceWizard import NewDeviceWizard
from ATE.org.actions_on.product.NewProductWizard import NewProductWizard
from ATE.org.actions_on.flow.HTOL.htolwizard import HTOLWizard
from ATE.org.actions_on.tests.TestWizard import TestWizard
from ATE.org.actions_on.program.TestProgramWizard import TestProgramWizard

from tests.qt.qualification_wizard import mock_db_object

import os
import shutil

import pytest
from pytestqt.qt_compat import qt_api

from PyQt5 import QtCore, QtWidgets


definitions = {'hardware': 'HW0',
               'maskset': 'Mask1',
               'die': 'Die1',
               'package': 'Package1',
               'device': 'Device1',
               'product': 'Product1',
               'test': 'ABC',
               'test1': 'CBA'}


# TODO: edit wizard is planned for future extension to cover more cases
test_configruation = {'name': definitions['test'],
                      'hardware': definitions['hardware'],
                      'type': 'custom',
                      'base': 'FT',
                      'owner': 'Production_FT',
                      'prog_name': 'HW0_FT_Device1_P_1',
                      'input_parameters': {'T': {'Min': -40, 'Max': 170, 'Default': 25, 'Unit': '°C'}},
                      'output_parameters': {'parameter2_name': {'LSL': 0, 'USL': None, 'Nom': 2.5, 'Unit': 'mV'}},
                      'docstring': 'test ABC'}


def debug_message(message):
    qt_api.qWarning(message)


# using this function when running CI build will block for ever
# !!! DON'T !!!
# just for localy debuging purposes
def debug_visual(window, qtbot):
    window.show()
    qtbot.stopForInteraction()


@pytest.fixture(scope='module')
def project_navigation():
    root_name = os.path.dirname(__file__)
    dir_name = os.path.join(root_name, 'smoke_test')
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    with ProjectNavigation(dir_name, root_name, None) as project_info:
        yield project_info

    # shutil.rmtree(dir_name)


@pytest.fixture(scope='module')
def model(project_navigation):
    model = TreeModel(project_navigation)
    return model


@pytest.fixture(scope='module')
def toolbar(project_navigation):
    toolbar = ToolBar(project_navigation)
    return toolbar


@pytest.fixture
def project(qtbot, project_navigation):
    dialog = ProjectWizard(None, project_navigation, 'New Project')
    qtbot.addWidget(dialog)
    return dialog


def test_create_new_project_cancel_before_enter_name(project, qtbot):
    qtbot.mouseClick(project.CancelButton, QtCore.Qt.LeftButton)


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
    dialog = HTOLWizard(mock_db_object.MockDBObject({"product": definitions['product']}), project_navigation)
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


def test_update_toolbar_paramster_not_base_and_target(model):
    model.apply_toolbar_change(definitions['hardware'], '', '')
    assert model.tests_section._is_hidden
    assert model.flows._is_hidden


def test_update_toolbar_parameters_with_base_and_target(qtbot, model, project_navigation):
    model.tests_section.observer = FakeObserver()
    with qtbot.waitSignal(project_navigation.toolbar_changed, timeout=500):
        project_navigation.update_toolbar_elements(definitions['hardware'], 'PR', definitions['product'])
        assert not model.tests_section._is_hidden
        assert not model.flows._is_hidden


@pytest.fixture
def new_test(qtbot, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = 'PR'
    dialog = TestWizard(project_navigation)
    qtbot.addWidget(dialog)
    return dialog


# def test_create_new_test_cancel_before_enter_name(new_test, qtbot):
#     qtbot.mouseClick(new_test.CancelButton, QtCore.Qt.LeftButton)


# def test_create_new_test_enter_name(new_test, qtbot):
#     with qtbot.waitSignal(new_test.TestName.textChanged, timeout=500):
#         qtbot.keyClicks(new_test.TestName, definitions['test'])

#     qtbot.mouseClick(new_test.OKButton, QtCore.Qt.LeftButton)


# def test_does_test_exist(project_navigation):
#     assert project_navigation.get_test_state(definitions['test'])


@pytest.fixture
def new_test_program(mocker, qtbot, project_navigation):
    project_navigation.active_hardware = definitions['hardware']
    project_navigation.active_base = test_configruation['base']
    project_navigation.active_target = definitions['device']
    mocker.patch.object(ProjectNavigation, 'get_devices_for_hardware', return_value=[definitions['device']])
    dialog = TestProgramWizard(project_navigation, test_configruation['owner'])
    qtbot.addWidget(dialog)
    return dialog


# def test_create_new_test_program_cancel_before_enter_name(new_test_program, qtbot):
#     qtbot.mouseClick(new_test_program.CancelButton, QtCore.Qt.LeftButton)


# def test_create_new_test_program_enter_name(new_test_program, qtbot):
#     new_test_program.availableTests.addItem(definitions['test'])
#     new_test_program.availableTests.addItem(definitions['test1'])
#     # new_test_program._verify()

#     # TODO: find cleaner way to select items
#     new_test_program.availableTests.item(0).setSelected(True)
#     QtTest.QTest.mouseClick(new_test_program.testAdd, QtCore.Qt.LeftButton)
#     QtTest.QTest.mouseClick(new_test_program.testAdd, QtCore.Qt.LeftButton)
#     new_test_program.availableTests.item(0).setSelected(False)

#     # new_test_program.availableTests.item(1).setSelected(True)
#     # QtTest.QTest.mouseClick(new_test_program.testAdd, QtCore.Qt.LeftButton)

#     # sieht hier richtig aus aber schreibt nur einen Eintrag in der DB
#     # debug_visual(new_test_program, qtbot)
#     QtTest.QTest.mouseClick(new_test_program.OKButton, QtCore.Qt.LeftButton)


#def test_does_test_program_exist(project_navigation):
#    assert project_navigation.get_programs_for_hardware(definitions['hardware'])


# def test_does_test_target_exist(project_navigation):
#     assert True
#     # assert len(project_navigation.get_available_test_targets(test_configruation['hardware'], test_configruation['base'], definitions['test']))
#     # assert len(project_navigation.get_available_test_targets(test_configruation['hardware'], test_configruation['base'], definitions['test1']))


# @pytest.fixture
# def edit_test_program(mocker, qtbot, project_navigation):
#     dialog = EditTestProgramWizard(test_configruation['prog_name'], project_navigation, test_configruation['owner'])
#     qtbot.addWidget(dialog)
#     return dialog


# def test_edit_test_program(edit_test_program, qtbot):
#     edit_test_program.availableTests.addItem(definitions['test'])
#     edit_test_program.availableTests.item(0).setSelected(True)
#     QtTest.QTest.mouseClick(edit_test_program.testAdd, QtCore.Qt.LeftButton)

#     # debug_message(edit_test_program.prog_name)
#     # debug_visual(edit_test_program, qtbot)
