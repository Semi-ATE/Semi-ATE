# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
ATE status bar widgets.
"""

# Third-party imports
from qtpy.QtCore import Signal
from spyder.api.widgets.status import StatusBarWidget


class ATEStatusBar(StatusBarWidget):
    ID = 'ate_statusbar'

    sig_update_value = Signal(str)

    def __init__(self, parent=None, show_icon=False, show_label=True,
                 show_spinner=False):
        super().__init__(parent, show_icon, show_label, show_spinner)
        self.sig_update_value.connect(self.set_value)

    def get_tooltip(self) -> str:
        return 'ATE plugin status messages'
