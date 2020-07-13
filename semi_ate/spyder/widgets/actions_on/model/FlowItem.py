from ATE.org.actions_on.model.BaseItem import BaseItem as BaseItem
from ATE.org.actions_on.model.Constants import MenuActionTypes

flows = ['checker', 'maintenance', 'production', 'engineering', 'validation', 'quality']


def generate_item_name(item):
    # construct a unique name for this item. Since SimpleItems
    # exist in multiple versions with the same basic name, we construct
    # the name based on
    # - the given name
    # - the active target
    # - the active base
    if None in [item.project_info.active_target, item.project_info.active_base]:
        return None

    owner_name = item.project_info.active_hardware.upper() + '_' + item.project_info.active_base.upper() + '_' + item.project_info.active_target + '_' + get_prefix(item)
    return owner_name


def get_prefix(item):
    if item.text() in flows:
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
        item.appendRow(TestprogramTreeItem(item.project_info, program, owner_name, index))


def add_testprogram_impl(project_info, item):
    import ATE.org.actions_on.program.TestProgramWizard as new_prog
    new_prog.new_program_dialog(project_info, get_prefix(item), None)


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
        owner_name = generate_item_name(self)

        programs = self.project_info.get_programs_for_owner(owner_name)
        for index, program in enumerate(programs):
            self.appendRow(TestprogramTreeItem(self.project_info, program, owner_name, index))

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
            self.appendRow(QualiFlowSubitemInstance(self.project_info, subflow, self.project_info.active_target, subflow.get_definition(), self.modname, self))

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
        constraint_func = getattr(self.mod, "check_delete_constraints")
        if constraint_func is not None:
            if constraint_func(self.project_info, self.data) is False:
                return
        self.project_info.delete_qualification_flow_instance(self.data)

    def add_testprogram(self):
        add_testprogram_impl(self.project_info, self)

    def _generate_sub_items(self):
        append_test_program_nodes(self)


class TestprogramTreeItem(BaseItem):
    def __init__(self, project_info, program, owner, order):
        super().__init__(project_info, program.prog_name, None)
        self.owner = owner
        self.order = order

    def _get_menu_items(self):
        return [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                MenuActionTypes.MoveUp(),
                MenuActionTypes.MoveDown(),
                None,
                MenuActionTypes.Delete()]

    def edit_item(self):
        import ATE.org.actions_on.program.EditTestProgramWizard as edit
        edit.edit_program_dialog(self.text(), self.project_info, self.owner)

    def display_item(self):
        import ATE.org.actions_on.program.ViewTestProgramWizard as view
        view.view_program_dialog(self.text(), self.project_info, self.owner)

    def delete_item(self):
        self.project_info.delete_program(self.text(), self.owner, self.order)

    def move_up_item(self):
        self.project_info.move_program(self.text(), self.owner, self.order, True)

    def move_down_item(self):
        self.project_info.move_program(self.text(), self.owner, self.order, False)
