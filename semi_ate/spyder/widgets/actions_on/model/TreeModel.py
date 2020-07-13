from PyQt5 import QtCore, QtGui

from ATE.org.actions_on.model.BaseItem import BaseItem
from ATE.org.actions_on.model import FlowItem as FlowItem
from ATE.org.actions_on.tests.TestItem import TestItem
from ATE.org.constants import TableIds
from ATE.org.plugins.pluginmanager import get_plugin_manager


class TreeModel(QtGui.QStandardItemModel):
    edit_file = QtCore.pyqtSignal(["QString"])
    delete_file = QtCore.pyqtSignal(["QString"])

    def __init__(self, project_info, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setHorizontalHeaderLabels([self.tr("Project")])
        self.project_info = project_info
        self.hardware = ''
        self.base = ''
        self.target = ''

        self.plugin_manager = get_plugin_manager()

        installed_plugins = self.plugin_manager.hook.get_plugin_identification()
        print("Installed plugins:")
        print(installed_plugins)

        import os
        self.doc_path = os.path.join(self.project_info.project_directory, "doc")
        self.tests_path = os.path.join(self.project_info.project_directory, "src")
        self._setup()
        self._connect_action_handler()

        hardware, base, target = self.project_info.load_project_settings()
        # hack: trigger signal to update the toolbar components
        self.project_info.update_settings.emit(hardware, base, target)

        self.update(hardware, base, target)

    @QtCore.pyqtSlot(int)
    def on_db_change(self, table_id):
        if table_id == TableIds.Flow():
            self.flows.update()

        # TODO: update the test section musst be done differently to prevent collapsing
        #       child-items
        if table_id == TableIds.NewTest():
            self.tests_section.update()

        if table_id == TableIds.Test():
            self._update_tests()

        if table_id == TableIds.Die() or \
           table_id == TableIds.Device():
            self.project_info.update_target.emit()

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
        self.project_info.database_changed.connect(self.on_db_change)
        self.project_info.toolbar_changed.connect(self.apply_toolbar_change)
        self.project_info.select_target.connect(self._update_test_items)
        self.project_info.select_base.connect(self._update_test_section)
        self.project_info.select_hardware.connect(self._update_test_items_hw_changed)
        self.project_info.test_target_deleted.connect(self._remove_test_target_item)

    @QtCore.pyqtSlot(str)
    def _update_test_section(self, base):
        self.tests_section.update()

    @QtCore.pyqtSlot(str, str, str)
    def apply_toolbar_change(self, hardware, base, target):
        rebuild_flows = self.target != target
        self.hardware = hardware
        self.base = base
        self.target = target

        self.flows.update()
        self._update_tests()

        if rebuild_flows:
            self._reset_flows(self.project_info)

    def _setup(self):
        project_name = self.project_info.project_name
        if project_name is None or '':
            project_name = "No Project"

        self.root_item = SectionItem(self.project_info, project_name)
        self._setup_definitions()
        self._setup_documentation()
        self._setup_flow_items(self.project_info)
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

        self.production_flows = FlowItem.SimpleFlowItem(project_info, "checker")
        self.flows.appendRow(self.production_flows)
        self.production_flows = FlowItem.SimpleFlowItem(project_info, "maintenance")
        self.flows.appendRow(self.production_flows)
        self.production_flows = FlowItem.SimpleFlowItem(project_info, "production")
        self.flows.appendRow(self.production_flows)
        self.engineering_flows = FlowItem.SimpleFlowItem(project_info, "engineering")
        self.flows.appendRow(self.engineering_flows)
        self.validation_flows = FlowItem.SimpleFlowItem(project_info, "validation")
        self.flows.appendRow(self.validation_flows)
        self.characterisation_flows = FlowItem.SimpleFlowItem(project_info, "quality")
        self.flows.appendRow(self.characterisation_flows)

        if self.base == "FT":

            package = ''
            if self.target != '':
                package = self.project_info.get_device_package(self.target)

            self.quali_flows = FlowItem.FlowItem(project_info, "qualification", self.flows)
            self.quali_flows.appendRow(FlowItem.SimpleFlowItem(project_info, "ZHM", "Zero Hour Measurements"))
            self.quali_flows.appendRow(FlowItem.SimpleFlowItem(project_info, "ABSMAX", "Absolute Maximum Ratings"))

            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.EC.ecwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.HTOL.htolwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.HTSL.htslwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.DR.drwizard"))
            self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.AC.acwizard"))

            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.HAST.hastwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.ELFR.elfrwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.LU.luwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.TC.tcwizard"))
            self.quali_flows.appendRow(self._make_single_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.THB.thbwizard"))

            if not self.project_info.is_package_a_naked_die(package):
                self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.ESD.esdwizard"))
                self.quali_flows.appendRow(self._make_multi_instance_quali_flow_item(project_info, "ATE.org.actions_on.flow.RSH.rshwizard"))

            self.flows.appendRow(self.quali_flows)

    def _make_single_instance_quali_flow_item(self, parent, module):
        return FlowItem.SingleInstanceQualiFlowItem(parent, "Tmp", module)

    def _make_multi_instance_quali_flow_item(self, parent, module):
        return FlowItem.MultiInstanceQualiFlowItem(parent, "Tmp", module)

    def _setup_documentation(self):
        from ATE.org.actions_on.documentation.DocumentationObserver import DocumentationObserver
        from ATE.org.actions_on.documentation.DocumentationItem import DocumentationItem
        # TODO: do we need a sorting-order (alphabetic, etc...) ?
        self.documentation_section = DocumentationItem("documentation", self.doc_path, is_editable=False)
        self.doc_observer = DocumentationObserver(self.doc_path, self.documentation_section)
        self.doc_observer.start_observer()

        self.root_item.insert_item(self.documentation_section)

    def _update_definitions(self):
        self.definition_section.update()

    def _setup_definitions(self):
        from ATE.org.actions_on.hardwaresetup.HardwaresetupItem import HardwaresetupItem
        from ATE.org.actions_on.maskset.MasksetItem import MasksetItem
        from ATE.org.actions_on.die.DieItem import DieItem
        from ATE.org.actions_on.package.PackageItem import PackageItem
        from ATE.org.actions_on.device.DeviceItem import DeviceItem
        from ATE.org.actions_on.product.ProductItem import ProductItem
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

        if self.die.has_children():
            self.die.set_children_hidden(False)
        else:
            if self.maskset.has_children() and \
               self.hardwaresetup.has_children():
                self.die.set_children_hidden(False)
            else:
                self.die.set_children_hidden(True)

        # device update state
        if self.device.has_children():
            self.device.set_children_hidden(False)
        else:
            if self.die.has_children() and \
               self.package.has_children() and \
               self.hardwaresetup.has_children():
                self.device.set_children_hidden(False)
            else:
                self.device.set_children_hidden(True)

        # product update state
        if self.product.has_children():
            self.product.set_children_hidden(False)
        else:
            if self.device.has_children() and \
               self.hardwaresetup.has_children():
                self.product.set_children_hidden(False)
            else:
                self.product.set_children_hidden(True)

        self._reset_flows(self.project_info)

    def _setup_tests(self):
        self.tests_section = TestItem(self.project_info, "tests", self.tests_path, self)
        self.root_item.appendRow(self.tests_section)

    def _update_tests(self):
        if not self.tests_section.is_enabled():
            self.tests_section.update()

        self._update_test_items(self.project_info.active_target)

    @QtCore.pyqtSlot(str)
    def _update_test_items(self, text):
        for index in range(self.tests_section.rowCount()):
            item = self.tests_section.child(index)

            available_test_targets_for_current_test_item = item.get_available_test_targets()
            actual_test_targets_for_current_test_item = item.get_children()
            new_items = list(set(available_test_targets_for_current_test_item) - set(actual_test_targets_for_current_test_item))

            for new_item in new_items:
                item.add_target_item(new_item)

            for test_target_index in range(item.rowCount()):
                test_target_item = item.child(test_target_index)
                if test_target_item is None:
                    continue

                test_target_item.update_state(text)

    @QtCore.pyqtSlot(str, str)
    def _remove_test_target_item(self, target_name, test_name):
        for index in range(self.tests_section.rowCount()):
            test_item = self.tests_section.child(index)
            if test_item.text() != test_name:
                continue

            for test_target_index in range(test_item.rowCount()):
                test_target_item = test_item.child(test_target_index)
                if test_target_item is None or target_name != test_target_item.text():
                    continue

                test_target_item.clean_up()
                test_item.removeRow(test_target_index)

    @QtCore.pyqtSlot(str)
    def _update_test_items_hw_changed(self, hardware):
        for index in range(self.tests_section.rowCount()):
            self.tests_section.takeChild(index)

        self.tests_section.update()

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
