from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem as BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)
from ate_spyder.widgets.constants import SUBFLOWS_QUALIFICATION, FLOWS

from PyQt5 import QtGui, QtCore
import os


def generate_item_name(item):
    # construct a unique name for this item. Since SimpleItems
    # exist in multiple versions with the same basic name, we construct
    # the name based on
    # - the given name
    # - the active target
    # - the active base
    if None in [item.project_info.active_target, item.project_info.active_base]:
        return None

    groups = [group.name for group in item.project_info.get_groups()]
    if item.text() in groups:
        return item.project_info.active_hardware.upper() + '_' + item.project_info.active_base.upper() + '_' + item.project_info.active_target + '_' + item.text()

    # sub_qualification items
    if item.text() in SUBFLOWS_QUALIFICATION:
        return item.project_info.active_hardware.upper() + '_' + item.project_info.active_base.upper() + '_' + item.project_info.active_target + '_' + 'qualification' + '_' + item.text()

    # sub_sub_qualification items
    return item.project_info.active_hardware.upper() + '_' + item.project_info.active_base.upper() + '_' + item.project_info.active_target + '_' + 'qualification' + '_' + item.parent.text() + '_' + item.text()


def get_prefix(item):
    if item.text() in FLOWS:
        prefix = item.text()[0].upper()
    else:
        if item.parent is not None:
            prefix = item.parent.text() + '_' + item.text()
        else:
            prefix = item.text()

    return prefix


def append_test_program_nodes(item):
    owner_name = generate_item_name(item)

    programs = item.project_info.get_programs_for_owner(owner_name)
    for index, program in enumerate(programs):
        item.appendRow(TestprogramTreeItem(item.project_info, program, owner_name, index, len(programs) == 1, item))


def add_testprogram_impl(project_info, item):
    import ate_spyder.widgets.actions_on.program.TestProgramWizard as new_prog
    handle_excpetions(project_info.parent,
                      lambda: new_prog.new_program_dialog(project_info, get_prefix(item), item),
                      ExceptionTypes.Program())


class FlowItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent)

    def update(self):
        if self.project_info.active_target == '' or self.project_info.active_target is None:
            self.set_children_hidden(True)
            return
        else:
            self.set_children_hidden(False)

        for c in range(int(0), self.row_count()):
            item = self.child(c)
            item.update()

    def remove_flow(self, name: str):
        for index in range(self.rowCount()):
            flow_item = self.child(index)

            if flow_item.text() != name:
                continue

            self.removeRow(flow_item.row())


class SimpleFlowItem(FlowItem):
    '''
        The simple flow item is any flow item which
        only has flow instances (i.e. testprograms!)
        as children.
    '''
    def __init__(self, project_info, name, tooltip=""):
        super().__init__(project_info, name, None)
        self.setToolTip(tooltip)

    def update(self):
        super().update()
        self.removeRows(0, self.row_count())
        append_test_program_nodes(self)

    def _get_children_names(self):
        return self.project_info.get_programs_for_owner(generate_item_name(self))

    def _append_children(self):
        append_test_program_nodes(self)

    def add_testprogram(self):
        add_testprogram_impl(self.project_info, self)

    def _get_menu_items(self):
        return [MenuActionTypes.AddTestprogram()]


class QualiFlowItemBase(FlowItem):
    def __init__(self, project_info, name, implmodule, parent=None):
        super().__init__(project_info, name, parent)
        import importlib
        self.mod = importlib.import_module(implmodule)
        self.setToolTip(getattr(self.mod, "quali_flow_tooltip"))
        self.setText(getattr(self.mod, "quali_flow_listentry_name"))
        self.flowname = (getattr(self.mod, "quali_flow_name"))
        self.modname = implmodule
        self._generate_sub_items()

    def _generate_sub_items(self):
        pass

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]


class SingleInstanceQualiFlowItem(QualiFlowItemBase):
    def _get_menu_items(self):
        return [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                None,
                MenuActionTypes.AddTestprogram()]

    def edit_item(self):
        edit_func = getattr(self.mod, "edit_item")
        edit_func(self.project_info, self.project_info.active_target)

    def view_item(self):
        edit_func = getattr(self.mod, "view_item")
        edit_func(self.project_info, self.project_info.active_target)

    def update(self):
        super().update()
        self.removeRows(0, self.row_count())
        self._generate_sub_items()

    def add_testprogram(self):
        add_testprogram_impl(self.project_info, self)
        self.update()

    def _generate_sub_items(self):
        append_test_program_nodes(self)


class MultiInstanceQualiFlowItem(QualiFlowItemBase):
    def __init__(self, project_info, name, implmodule, parent=None):
        super().__init__(project_info, name, implmodule, parent)

    def update(self):
        super().update()
        self.removeRows(0, self.row_count())
        self._generate_sub_items()

    def _generate_sub_items(self):
        for subflow in self.project_info.get_data_for_qualification_flow(self.flowname, self.project_info.active_target):
            self.appendRow(QualiFlowSubitemInstance(self.project_info, subflow, self.project_info.active_target, subflow, self.modname, self))

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]

    def new_item(self):
        new_func = getattr(self.mod, "new_item")
        new_func(self.project_info, self.project_info.active_target)


class QualiFlowSubitemInstance(BaseItem):
    def __init__(self, project_info, subflow, product, data, implmodule, parent):
        super().__init__(project_info, subflow.name, parent)
        import importlib
        self.mod = importlib.import_module(implmodule)
        self.product = product
        self.data = subflow
        self._generate_sub_items()

    def _get_menu_items(self):
        return [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                MenuActionTypes.Delete(),
                None,
                MenuActionTypes.AddTestprogram()]

    def edit_item(self):
        edit_func = getattr(self.mod, "edit_item")
        edit_func(self.project_info, self.data)

    def display_item(self):
        edit_func = getattr(self.mod, "view_item")
        edit_func(self.project_info, self.data)

    def delete_item(self):
        constraint_func = getattr(self.mod, "check_delete_constraints", None)
        if constraint_func is not None:
            if constraint_func(self.project_info, self.data) is False:
                return

        for child_index in range(self.rowCount()):
            item = self.child(child_index)
            # do not update the tree to prevent reinstantiation of qualification flow items
            # therefore self do not point to the same item any more !!
            item.delete_program(emit_event=False)

        self.project_info.delete_qualification_flow_instance(self.data)

    def add_testprogram(self):
        add_testprogram_impl(self.project_info, self)

    def _generate_sub_items(self):
        append_test_program_nodes(self)


class TestprogramTreeItem(BaseItem):
    def __init__(self, project_info: ProjectNavigation, program: str, owner: str, order: int, is_single: bool, parent: QtGui.QStandardItem):
        self.program_name = program.prog_name
        super().__init__(project_info, self.program_name, None)
        self.owner = owner
        self.order = order
        self.parent = parent
        self.is_single = is_single

        if not self._is_test_program_valid():
            self.setData(QtGui.QColor(255, 0, 0), QtCore.Qt.ForegroundRole)

    def _get_menu_items(self):
        menu = [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                MenuActionTypes.CopyPath(),
                None,
                MenuActionTypes.Delete()]

        if not self.is_single:
            menu.insert(2, MenuActionTypes.MoveDown())
            menu.insert(2, MenuActionTypes.MoveUp())

        return menu

    @staticmethod
    def is_valid_functionality(functionality):
        if functionality in (MenuActionTypes.MoveDown(), MenuActionTypes.MoveUp()):
            return False

        return True

    def edit_item(self):
        import ate_spyder.widgets.actions_on.program.EditTestProgramWizard as edit
        handle_excpetions(self.project_info.parent,
                          lambda: edit.edit_program_dialog(self.text(), self.project_info, self.owner, self.parent),
                          ExceptionTypes.Program())

    def display_item(self):
        import ate_spyder.widgets.actions_on.program.ViewTestProgramWizard as view
        handle_excpetions(self.project_info.parent,
                          lambda: view.view_program_dialog(self.text(), self.project_info, self.owner, self.parent),
                          ExceptionTypes.Program())

    def delete_program(self, emit_event=True):
        from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace

        targets = self.project_info.get_depandant_test_target_for_program(self.text())
        if not ItemTrace(targets, self.text(), self.project_info.parent, message="the above target(s) are going to be\ndeleted !").exec_():
            return

        self.project_info.delete_program(self.text(), self.owner, self.order, emit_event)

    def delete_item(self):
        self.delete_program()

    def move_up_item(self):
        self.project_info.move_program(self.text(), self.owner, self.order, True)

    def move_down_item(self):
        self.project_info.move_program(self.text(), self.owner, self.order, False)

    def _is_test_program_valid(self):
        return self.project_info.is_test_program_valid(self.text())

    def copy_absolute_path(self):
        clip_board = QtGui.QGuiApplication.clipboard()
        clip_board.clear(mode=clip_board.Clipboard)
        from pathlib import Path
        file_path = os.fspath(Path(os.path.join(self.project_info.project_directory,
                                                'src',
                                                self.project_info.active_hardware,
                                                self.project_info.active_base,
                                                f'{self.program_name}.py')))

        clip_board.setText(file_path, mode=clip_board.Clipboard)
