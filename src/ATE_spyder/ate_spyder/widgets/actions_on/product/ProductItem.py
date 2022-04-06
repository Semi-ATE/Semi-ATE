from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.product.EditProductWizard import edit_product_dialog
from ate_spyder.widgets.actions_on.product.NewProductWizard import new_product_dialog
from ate_spyder.widgets.actions_on.product.ViewProductWizard import display_product_settings_dialog
from ate_spyder.widgets.actions_on.utils.StateItem import StateItem

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)


class ProductItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

    def _get_children_names(self):
        return self.project_info.get_products()

    def _create_child(self, name, parent):
        return ProductItemChild(self.project_info, name, parent)

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_product_dialog(self.project_info),
                          ExceptionTypes.Product())


class ProductItemChild(StateItem):
    def __init__(self, project_info, productdata, parent=None):
        super().__init__(project_info, productdata, parent=parent)

    def edit_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: edit_product_dialog(self.project_info, self.text()),
                          ExceptionTypes.Product())

    def display_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: display_product_settings_dialog(self.text(), self.project_info),
                          ExceptionTypes.Product())

    def is_enabled(self):
        return self.project_info.get_product_state(self.text())

    def _update_db_state(self, enabled):
        self.project_info.update_product_state(self.text(), enabled)

    def _are_dependencies_fulfilled(self):
        dependency_list = {}
        # ToDo: Avoid this, instead retrieve product and read out the properties needed.
        hw = self.project_info.get_product_hardware(self.text())
        device = self.project_info.get_product_device(self.text())
        hw_enabled = self.project_info.get_hardware_state(hw)
        device_enabled = self.project_info.get_device_state(device)

        if not hw_enabled:
            dependency_list.update({'hardwares': hw})
        if not device_enabled:
            dependency_list.update({'devices': device})

        return dependency_list

    def _enabled_item_menu(self):
        return [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                None,
                self._dependant_menu_type()]

    # TODO: should we be able to delete product oder just make it obsolete,
    # but how to say if the product not used at all
    @property
    def type(self):
        return 'products'

    @property
    def dependency_list(self):
        return {}
