from qtpy import QtCore
from qtpy import QtGui
from qtpy.QtCore import Signal

from ate_spyder.widgets.actions_on.model import FlowItem as FlowItem
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.constants import TableIds
from ate_semiateplugins.pluginmanager import get_plugin_manager
from ate_spyder.widgets.actions_on.model.sections.TestSection import TestSection

from ate_spyder.widgets.actions_on.model.FileItemHandler import FileItemHandler


QualificationFlow = 'qualification'


class TreeModel(QtGui.QStandardItemModel):
    edit_file = Signal(str)
    delete_file = Signal(str)
    edit_test_params = Signal(str)

    def __init__(self, project_info, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setHorizontalHeaderLabels([self.tr("Project")])
        self.project_info = project_info
        self.hardware = ''
        self.base = ''
        self.target = ''
        self.folder_sections = []

        self.plugin_manager = get_plugin_manager()

        installed_plugins = self.plugin_manager.hook.get_plugin_identification()
        print("Installed plugins:")
        print(installed_plugins)

        import os
        self.doc_path = os.path.join(self.project_info.project_directory, "doc")
        self.base_path = os.path.join(self.project_info.project_directory, "src")

        self.file_item_handler = FileItemHandler(self.project_info, self.base_path)
        self._setup()
        self._connect_action_handler()

        hardware, base, target = self.project_info.load_project_settings()
        self.project_info.update_toolbar_elements(hardware, base, target)
        self.parent.update_settings.emit(hardware, base, target)

        self.update(hardware, base, target)

    @QtCore.Slot(int)
    def on_db_change(self, table_id):
        if table_id == TableIds.Flow():
            self.flows.update()

        # TODO: update the test section must be done differently to prevent collapsing
        #       child-items
        if table_id == TableIds.NewTest():
            self.tests_section.update()

        if table_id == TableIds.Test():
            self._update_tests()

        if table_id == TableIds.Die() or \
           table_id == TableIds.Device():
            self.project_info.parent.update_target.emit()

        # Note: This will basically rebuild the complete "definitions"
        # subtree. We might get performance problems here, if we ever
        # encounter a project with *lots* of definition items. If
        # this ever happens we can split updating the trees into
        # individual subtrees using the table_id and calling update
        # only on the matching subtree node.
        if table_id in [TableIds.Definition(), TableIds.Hardware(),
                        TableIds.Maskset(), TableIds.Device(),
                        TableIds.Die(), TableIds.Package(),
                        TableIds.Product()]:
            self._update_definitions()
            self.update(self.hardware, self.base, self.target)

    def _connect_action_handler(self):
        self.itemChanged.connect(lambda item: self._update(item, self.hardware, self.base, self.target))
        self.parent.database_changed.connect(self.on_db_change)
        self.parent.toolbar_changed.connect(self.apply_toolbar_change)
        self.parent.select_target.connect(self._update_test_items)
        self.parent.select_base.connect(self._update_test_section)
        self.parent.select_hardware.connect(self._update_test_items_hw_changed)
        self.parent.test_target_deleted.connect(self._remove_test_target_item)
        self.parent.group_state_changed.connect(self._update_test_section)
        self.parent.group_added.connect(self._add_group)
        self.parent.group_removed.connect(self._remove_group)
        self.parent.groups_update.connect(self._update_groups)

    @QtCore.Slot(str)
    def _update_test_section(self, base):
        self.tests_section.update()

    @QtCore.Slot()
    def _update_test_section(self):
        self.tests_section.update()

    @QtCore.Slot(str, str, str)
    def apply_toolbar_change(self, hardware, base, target):
        rebuild_flows = self.target != target
        self.hardware = hardware
        self.base = base
        self.target = target

        self.flows.update()
        self._update_tests()

        if rebuild_flows:
            self._reset_flows(self.project_info)

    @QtCore.Slot(str)
    def _add_group(self, name):
        self.new_group_flow = FlowItem.SimpleFlowItem(self.project_info, name)
        self.flows.appendRow(self.new_group_flow)

    @QtCore.Slot(str)
    def _remove_group(self, name):
        self.flows.remove_flow(name)

    @QtCore.Slot(str, list)
    def _update_groups(self, name, groups):
        self.tests_section.update_group_items(name, groups)

    def _setup(self):
        project_name = self.project_info.project_name
        if project_name is None or '':
            project_name = "No Project"
            return

        self.root_item = SectionItem(self.project_info, project_name)
        self._setup_definitions()
        self._setup_documentation()
        self._setup_flow_items(self.project_info)
        self._setup_file_collector_items()
        self._setup_protocol_item()
        self._setup_tests()
        self.appendRow(self.root_item)

    def _setup_flow_items(self, project_info):
        self.flows = FlowItem.FlowItem(project_info, "flows")
        self.root_item.appendRow(self.flows)
        # Make sure the items have the correct state with respect to
        # the current toolbar state
        self._reset_flows(project_info)
        self.flows.update()

    def _reset_flows(self, project_info):
        self.flows.removeRows(0, self.flows.row_count())
        if self.base == '' or self.target == '':
            self.flows.set_children_hidden(True)
            return

        self.flows.set_children_hidden(False)
        self._append_flows()

        if self.base == "FT":

            package = ''
            if self.target != '':
                package = self.project_info.get_device_package(self.target)

            self.quali_flows = FlowItem.FlowItem(project_info, "qualification", self.flows)
            self.quali_flows.appendRow(FlowItem.SimpleFlowItem(project_info, "ZHM", "Zero Hour Measurements"))
            self.quali_flows.appendRow(FlowItem.SimpleFlowItem(project_info, "ABSMAX", "Absolute Maximum Ratings"))

            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.EC.ecwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.HTOL.htolwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.HTSL.htslwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.DR.drwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.AC.acwizard"))

            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.HAST.hastwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.ELFR.elfrwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.LU.luwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.TC.tcwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.THB.thbwizard"))

            if not self.project_info.is_package_a_naked_die(package):
                self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.ESD.esdwizard"))
                self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ate_spyder.widgets.actions_on.flow.RSH.rshwizard"))

            self.flows.appendRow(self.quali_flows)

    def _append_flows(self):
        groups = self.project_info.get_groups()
        self.groups = []
        for group in groups:
            if group.name in (self.tests_section.text(), QualificationFlow):
                continue
            self.groups.append(FlowItem.SimpleFlowItem(self.project_info, group.name))

        for group in self.groups:
            self.flows.appendRow(group)

    def _make_single_instance_quali_flow_item(self, parent, module):
        return FlowItem.SingleInstanceQualiFlowItem(parent, "Tmp", module)

    def _make_multi_instance_quali_flow_item(self, parent, module):
        return FlowItem.MultiInstanceQualiFlowItem(parent, "Tmp", module)

    def _setup_documentation(self):
        from ate_spyder.widgets.actions_on.documentation.DocumentationObserver import DocumentationObserver
        from ate_spyder.widgets.actions_on.documentation.DocumentationItem import DocumentationItem
        # TODO: do we need a sorting-order (alphabetic, etc...) ?
        self.documentation_section = DocumentationItem("documentation", self.doc_path, self.project_info, is_editable=False)
        self.doc_observer = DocumentationObserver(self.doc_path, self.documentation_section)
        self.doc_observer.start_observer()

        self.root_item.insert_item(self.documentation_section)

    def _update_definitions(self):
        self.definition_section.update()

    def _setup_definitions(self):
        from ate_spyder.widgets.actions_on.hardwaresetup.HardwaresetupItem import HardwaresetupItem
        from ate_spyder.widgets.actions_on.maskset.MasksetItem import MasksetItem
        from ate_spyder.widgets.actions_on.die.DieItem import DieItem
        from ate_spyder.widgets.actions_on.package.PackageItem import PackageItem
        from ate_spyder.widgets.actions_on.device.DeviceItem import DeviceItem
        from ate_spyder.widgets.actions_on.product.ProductItem import ProductItem
        self.definition_section = SectionItem(self.project_info, "definitions")

        self.hardwaresetup = HardwaresetupItem(self.project_info, "hardwaresetups")
        self.definition_section.insert_item(self.hardwaresetup)

        self.maskset = MasksetItem(self.project_info, "masksets")
        self.definition_section.insert_item(self.maskset)

        self.die = DieItem(self.project_info, "dies")
        self.definition_section.insert_item(self.die)

        self.package = PackageItem(self.project_info, "packages")

        self.definition_section.insert_item(self.package)

        self.device = DeviceItem(self.project_info, "devices")
        self.definition_section.insert_item(self.device)

        self.product = ProductItem(self.project_info, "products")
        self.definition_section.insert_item(self.product)

        self.root_item.insert_item(self.definition_section)

    def _update(self, item, hw, base, target):
        self.update(hw, base, target)

    def update(self, hardware, base, target):
        # die update state
        self.hardware = hardware
        self.base = base
        self.target = target

        self._update_die_section()
        self._update_device_section()
        self._update_product_section()
        self._update_file_collector_section()

    def _update_device_section(self):
        if self.device.has_children():
            self.device.set_children_hidden(False)
        else:
            if self.die.has_children() and \
               self.package.has_children() and \
               self.hardwaresetup.has_children():
                self.device.set_children_hidden(False)
            else:
                self.device.set_children_hidden(True)

    def _update_product_section(self):
        if self.product.has_children():
            self.product.set_children_hidden(False)
        else:
            if self.device.has_children() and \
               self.hardwaresetup.has_children():
                self.product.set_children_hidden(False)
            else:
                self.product.set_children_hidden(True)

    def _update_file_collector_section(self):
        for folder_section in self.file_item_handler.items():
            if len(self.target) and len(self.base):
                folder_section.set_pattern_directory(self.hardware, self.base)
            else:
                folder_section.hide()

        self._reset_flows(self.project_info)

    def _update_die_section(self):
        if self.die.has_children():
            self.die.set_children_hidden(False)
        else:
            if self.maskset.has_children() and \
               self.hardwaresetup.has_children():
                self.die.set_children_hidden(False)
            else:
                self.die.set_children_hidden(True)

    def _setup_tests(self):
        self.tests_section = TestSection(self.project_info, "tests", self.base_path, self)
        self.root_item.appendRow(self.tests_section)

    def _update_tests(self):
        if not self.tests_section.is_enabled():
            self.tests_section.update()

        self._update_test_items(self.project_info.active_target)

    @QtCore.Slot(str)
    def _update_test_items(self, text):
        self.tests_section.update_test_items(text)

    @QtCore.Slot(str, str)
    def _remove_test_target_item(self, target_name: str, test_name: str):
        self.tests_section.remove_test_target_item(target_name, test_name)

    @QtCore.Slot(str)
    def _update_test_items_hw_changed(self, hardware):
        self.tests_section.update_test_items_hw_changed(hardware)

    def set_tree_items_state(self, name, dependency_list, enabled):
        for key, elements in dependency_list.items():
            if key == 'devices' or \
               key == 'dies' or \
               key == 'products':
                self.definition_section.get_child(key)._set_node_state(elements, enabled)
            if key == 'tests':
                self.tests_section._set_node_state(elements, enabled)
            if key == 'programs':
                pass

    def clean_up(self):
        self.doc_observer.stop_observer()
        self.tests_section.observer.stop_observer()
        self.file_item_handler.clean_up()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.clean_up()

    def _setup_file_collector_items(self):
        for file_item in self.file_item_handler.items():
            self.root_item.appendRow(file_item)

    def _setup_protocol_item(self):
        from ate_spyder.widgets.actions_on.protocol.ProtocolItem import ProtocolItem
        self.protocol_section = ProtocolItem('protocols', self.project_info)
        self.root_item.appendRow(self.protocol_section)


# ToDo: Move this class to its own file.
# Also: Check if it is really needed. The added value basically none
class SectionItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def insert_item(self, item):
        self.insertRow(0, item)

    def is_hidden(self):
        return True

    def is_editable(self):
        return True

    def update(self):
        for c in range(int(0), self.rowCount()):
            item = self.child(c)
            item.update()
