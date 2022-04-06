
from PyQt5 import QtWidgets


class HardwareWizardListItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, item_data):
        self.item_data = item_data
        super().__init__(parent, [item_data["display_name"]])
        self.setToolTip(0, f"{item_data['display_name']}, Source: {item_data['name']}")
