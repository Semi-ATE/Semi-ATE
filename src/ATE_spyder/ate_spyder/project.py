"""
Semi-ATE Project Types
"""
import os
import logging

from spyder.plugins.projects.api import BaseProjectType

logger = logging.getLogger(__name__)
# Third party imports


class ATEProject(BaseProjectType):
    ID = "Semi-ATE Project"

    @staticmethod
    def get_name():
        return "Semi-ATE Project"

    @staticmethod
    def validate_name(path, name):
        logger.debug(path, name)
        return True, ""

    def create_project(self):
        logger.debug(f"ATEProject : Creating Semi-ATE Project '{os.path.basename(self.root_path)}'")
        self.plugin.create_project(self.root_path)
        self.plugin.get_widget().toolbar.show()
        self.plugin.toggle_view(True)
        return True, ""

    def open_project(self):
        logger.debug(f"ATEProject : Opening Semi-ATE Project '{os.path.basename(self.root_path)}'")
        self.plugin.open_project(self.root_path)
        self.plugin.get_widget().toolbar.show()
        self.plugin.toggle_view(True)
        return True, ""

    def close_project(self):
        logger.debug(f"ATEProject : Closing Semi-ATE Project '{os.path.basename(self.root_path)}'")
        self.plugin.close_project()
        self.plugin.get_widget().toolbar.hide()
        self.plugin.toggle_view(False)
        return True, ""


class ATEPluginProject(BaseProjectType):
    ID = "Semi-ATE Plugin Project"

    @staticmethod
    def get_name():
        return "Semi-ATE Plugin Project"

    @staticmethod
    def validate_name(path, name):
        return True, ""

    def create_project(self):
        logger.debug(f"ATEPluginProject : Creating Semi-ATE Plugin Project '{os.path.basename(self.root_path)}'")
        from ate_spyder.widgets.plugins.New_Semi_ATE_Plugin_Wizard import New_Semi_ATE_Plugin_Dialog

        self.plugin.get_widget().toolbar.hide()
        # TODO: how to hide the ATE navigator ?

        status, retval = New_Semi_ATE_Plugin_Dialog(self.plugin.get_widget(), self.root_path)
        if status:  # OK
            logger.debug("ATEPluginProject: project created !!!!")
            return True, ""
        else:
            return False, "Project Creation Canceled."

    def open_project(self):
        logger.debug(f"ATEPluginProject : Opening Semi-ATE Plugin Project '{os.path.basename(self.root_path)}'")
        return True, ""

    def close_project(self):
        logger.debug("ATEPluginProject : Closing Semi-ATE Plugin Project '{os.path.basename(self.root_path)}'")
        return True, ""
