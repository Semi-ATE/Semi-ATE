"""
ATE Project Type.
"""

# Third party imports
from spyder.plugins.projects.api import BaseProjectType


class ATEProject(BaseProjectType):
    ID = "ate-project"

    @staticmethod
    def get_name():
        return "ATE test project"

    def create_project(self):
        # Available info
        print(self.root_path)
        print(self.projects_plugin)
        ate_plugin = self.get_plugin("ate")
        print("creating: ", ate_plugin)
        ate_plugin.get_widget().toolbar.show()
        ate_plugin.toggle_view(True)

    def open_project(self):
        ate_plugin = self.get_plugin("ate")
        print("opening: ", ate_plugin)
        ate_plugin.get_widget().toolbar.show()
        ate_plugin.toggle_view(True)

    def close_project(self):
        ate_plugin = self.get_plugin("ate")
        print("closing: ", ate_plugin)
        ate_plugin.get_widget().toolbar.hide()
        ate_plugin.toggle_view(False)
