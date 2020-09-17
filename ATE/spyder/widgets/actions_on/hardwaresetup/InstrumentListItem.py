
from PyQt5 import QtWidgets


class InstrumentListItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, instrument_data):
        self.instrument_data = instrument_data
        super().__init__(parent, [instrument_data["display_name"]])
        self.setToolTip(0, f"{instrument_data['display_name']}, Source: {instrument_data['name']}")
