"""
ATE Project Type.
"""

import os

# Third party imports
from spyder.plugins.projects.api import BaseProjectType


class ATEProject(BaseProjectType):
    ID = "ate-project"

    # Available info
    # self.root_path ➜ str, path to the root of the project
    # self.projects_plugin ➜ ?

    @staticmethod
    def get_name():
        return "ATE-test Project"

    @staticmethod
    def validate_name(path, name):
        return True, ""

    def create_project(self):
        """ This method is the entry point for creating an 'ATE project'."""
        print(f"Project : Creating ATE project '{os.path.basename(self.root_path)}'")
        self.plugin.create_project(self.root_path)
        self.plugin.get_widget().toolbar.show()
        self.plugin.toggle_view(True)
        return True, ""

    def open_project(self):
        print(f"Project : Opening ATE project '{os.path.basename(self.root_path)}'")
        self.plugin.open_project(self.root_path)
        self.plugin.get_widget().toolbar.show()
        self.plugin.toggle_view(True)
        return True, ""

    def close_project(self):
        print("Project : Closing ATE project '{os.path.basename(self.root_path)}'")
        self.plugin.close_project()
        self.plugin.get_widget().toolbar.hide()
        self.plugin.toggle_view(False)
        return True, ""
