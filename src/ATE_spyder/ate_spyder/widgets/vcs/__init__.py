# -*- coding: utf-8 -*-

# Copyright © Semi ATE

"""
Version Control System extensions.
"""

# Standard library imports
from typing import Optional, Tuple

# Qt-related imports
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QWidget


class VCSInitializationProvider(QWidget):
    """
    Base class that defines a basic interface to implement the required
    configuration for a version control system (VCS) linked to an ATE project.
    """

    NAME: Optional[str] = None
    """
    Unique constant name that identifies the provider.
    """

    RANK: int = -1
    """
    Preferred order of appearance in the project configuration dialog. Lower is
    higher.
    """

    sig_widget_changed = Signal()
    """
    Signal that indicates any change of status on any of the widgets defined
    by the configuration widget.

    Notes
    -----
    This signal must be connected to any widget that might change its status.
    """

    sig_update_status = Signal(bool, str)
    """
    Signal used to update the validity of the project dialog.

    Parameters
    ----------
    is_valid: bool
        True if the dialog should be enabled, False otherwise
    msg: Optional[str]
        Optional message to display.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ate_project_name: str = ''

    def set_ate_project_name(self, name: str):
        """Set the current ATE project name."""
        self.ate_project_name = name

    @classmethod
    def get_name(cls) -> str:
        """Retrieve the name of the VCS provider."""
        raise NotImplementedError(
            f'Class {cls.__qualname__} has not implemented the get_name '
            'method')

    def create_repository(self, project_path: str):
        """Perform actions related to repository creation/initialization."""
        raise NotImplementedError(
            f'Class {type(self).__qualname__} has not implemented the '
            'create_repository method')

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the status of the widget.

        Returns
        -------
        valid: bool
            True if the widget status is valid. False otherwise.
        msg: Optional[str]
            An optional message that displays the actions to take in order to
            set the widget into a valid state.
        """
        raise NotImplementedError(
            f'Class {type(self).__qualname__} has not implemented the '
            'validate method')
