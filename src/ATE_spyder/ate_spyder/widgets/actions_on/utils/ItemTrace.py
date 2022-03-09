import os
from typing import Dict, List, Union

from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog


class ItemTrace(BaseDialog):
    def __init__(self, dependency_list, name, parent, message=''):
        ui_file = '.'.join(os.path.realpath(__file__).split('.')[:-1]) + '.ui'
        super().__init__(ui_file, parent)
        self.dependency_list: Dict[str, Union[List[str], Dict[str, List[str]]]] = dependency_list
        self.name = name
        self.message = message
        self._setup()

    def _setup(self):
        self.setWindowTitle(self.name)
        self.feedback.setText(self.message)
        self.feedback.setStyleSheet('color: orange')
        self.tree_view.setHeaderHidden(True)
        for key, elements in self.dependency_list.items():
            parent = QtWidgets.QTreeWidgetItem(self.tree_view)
            parent.setText(0, key)
            parent.setExpanded(True)

            # special case as test-program could have the same name in different sections
            if key == "programs":
                for k in elements.keys():
                    p = self._generate_node(parent, k)
                    p.setExpanded(True)
                    for element in elements[k]:
                        self._generate_node(p, element)

                continue

            for element in elements:
                self._generate_node(parent, element)

        self.ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        self.cancel_button.clicked.connect(self.reject)

    def _generate_node(self, parent, name):
        node = QtWidgets.QTreeWidgetItem()
        node.setText(0, name)
        parent.addChild(node)
        return node
