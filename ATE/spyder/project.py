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
        return "Python ATE Project"

    def create_project(self):
        """ This method is the entry point for creating an 'ATE project'."""
        print(f"Project : Creating ATE project '{os.path.basename(self.root_path)}'")
        ate_plugin = self.get_plugin("ate")
        ate_plugin.create_project(self.root_path)
        ate_plugin.get_widget().toolbar.show()
        ate_plugin.toggle_view(True)

    def open_project(self):
        print(f"Project : Opening ATE project '{os.path.basename(self.root_path)}'")
        ate_plugin = self.get_plugin("ate")
        ate_plugin.open_project(self.root_path)
        ate_plugin.get_widget().toolbar.show()
        ate_plugin.toggle_view(True)

    def close_project(self):
        print("Project : Closing ATE project '{os.path.basename(self.root_path)}'")
        ate_plugin = self.get_plugin("ate")
        ate_plugin.close_project(self.root_path)
        ate_plugin.get_widget().toolbar.hide()
        ate_plugin.toggle_view(False)
