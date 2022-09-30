# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)

"""ATE STIL (IEEE 1450) main widget."""

# Standard library imports
import os
import os.path as osp
from datetime import datetime
import logging
from typing import List, Optional

# Third-party imports
import zmq
from qtpy.QtCore import Qt, Signal, QProcess, QSocketNotifier
from qtpy.QtWidgets import QWidget, QVBoxLayout

# Spyder imports
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.widgets.tabs import Tabs
from spyder.widgets.simplecodeeditor import SimpleCodeEditor

# Local imports
from ate_spyder_stil.api import STILActions
from ate_spyder.widgets.navigation import ProjectNavigation
from spyder.widgets.onecolumntree import OneColumnTree, OneColumnTreeActions


# Localization
_ = get_translation("spyder")

# Logging
logger = logging.getLogger(__name__)


class STILTree(OneColumnTree):
    pass


class STILContainer(PluginMainWidget):
    """STIL integration main widget."""

    ENABLE_SPINNER = True

    # ---- Signals
    sig_stil_compilation_started = Signal()
    """
    This signal indicates if the STIL compiler was invoked and is running.
    """

    sig_stil_compilation_stopped = Signal(bool)
    """
    This signal indicated if the STIL compiler has finished.

    Arguments
    ---------
    success: bool
        True if the compiler finished successfully. False otherwise.
    """

    def __init__(self, name, plugin, parent=None):
        super().__init__(name, plugin, parent)

        # Attributes
        self.project_info: Optional[ProjectNavigation] = None
        self.stil_process: Optional[QProcess] = None
        self.stil_process_running: bool = False

        self.zmq_context = zmq.Context.instance()
        self.stil_sock: zmq.Socket = self.zmq_context.socket(zmq.PULL)
        self.stil_port = self.stil_sock.bind_to_random_port('tcp://127.0.0.1')

        fid = self.stil_sock.getsockopt(zmq.FD)
        self.notifier = QSocketNotifier(fid, QSocketNotifier.Read, self)
        self.notifier.activated.connect(self.on_stil_msg_received)

        # Widgets
        self.tabwidget = Tabs(self)
        self.tabwidget.setTabsClosable(False)

        self.output_log = SimpleCodeEditor(self)
        self.output_log.setup_editor(language='None', wrap=True)
        self.output_log.setReadOnly(True)

        self.output_tree = STILTree(self)

        self.tabwidget.addTab(self.output_tree, _('Warnings/Errors'))
        self.tabwidget.addTab(self.output_log, _('Compilation log'))

        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.setLayout(layout)

    # --- PluginMainWidget API
    # ------------------------------------------------------------------------
    def get_title(self) -> str:
        return _('STIL')

    def get_focus_widget(self) -> QWidget:
        return self.tabwidget.currentWidget()

    def setup(self):
        # Actions
        self.run_stil_action = self.create_action(
            STILActions.RunSTIL, _('Compile STIL files'),
            self.create_icon('run_again'), tip=_('Compile STIL files'),
            triggered=self.compile_stil
        )

        self.run_stil_action.setEnabled(False)

    def update_actions(self):
        pass

    def on_close(self):
        return super().on_close()

    # --- Private API
    # ------------------------------------------------------------------------
    def compile_stil(self):
        if self.stil_process_running:
            self.stil_process.kill()
            return

        if not self.project_info:
            return

        self.output_log.clear()
        self.output_tree.clear()
        self.tabwidget.setCurrentIndex(1)

        now = datetime.now()
        self.publish_to_log(
            '----------------- '
            f'Compilation started {now.isoformat()} '
            '-----------------', skip_time=True
        )

        self.stil_process = QProcess(self)
        # self.stil_process.errorOccurred.connect(self.stil_process_failed)
        self.stil_process.finished.connect(self.stil_process_finished)

        # TODO: Determine STIL file location adequately
        project_path = self.project_info.project_directory
        cwd = osp.join(project_path, 'patterns')
        env = self.stil_process.processEnvironment()

        for var in os.environ:
            env.insert(var, os.environ[var])

        self.stil_process.setProcessEnvironment(env)
        self.stil_process.setWorkingDirectory(cwd)

        # Find STIL files recursively
        stil_files = []
        for root, _, files in os.walk(cwd):
            for file in files:
                _, ext = osp.splitext(file)
                ext = ext[1:]
                if ext == 'stil':
                    stil_files.append(osp.join(root, file))

        args = ['sscl', '--port', str(self.stil_port), '-c', '-i']
        args += stil_files

        self.stil_process.setProcessChannelMode(QProcess.SeparateChannels)
        self.stil_process.start(args[0], args[1:])
        self.stil_process_running = True
        self.run_stil_action.setIcon(self.create_icon('stop'))

    def stil_process_finished(self, exit_code, exit_status):
        self.stil_process_running = False
        self.stil_process = None
        self.run_stil_action.setIcon(self.create_icon('run_again'))

    def on_stil_msg_received(self):
        try:
            response = self.stil_sock.recv_json(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            return

        if response['kind'] == 'info':
            payload = response['payload']
            message = payload['message']
            logger.info(message)
            self.publish_to_log(message, level='INFO')

    # --- Public API
    # ------------------------------------------------------------------------
    def set_project_information(
            self, project_info: Optional[ProjectNavigation]):
        self.project_info = project_info

    def notify_project_status(self, ate_project_loaded: bool):
        self.run_stil_action.setEnabled(ate_project_loaded)

    def update_font(self, font, color_scheme):
        """
        Update font of the code editor.

        Parameters
        ----------
        font: QFont
            Font object.
        color_scheme: str
            Name of the color scheme to use.
        """
        self.output_log.set_color_scheme(color_scheme)
        self.output_log.set_font(font)

    def publish_to_log(self, msg: str, skip_time=False, level=None):
        prefix = ''
        if level is not None:
            prefix = f'{level} '
        if not skip_time:
            now = datetime.now()
            prefix = f'{prefix}{now.isoformat()} - '
        text = self.output_log.toPlainText()
        line_sep = self.output_log.get_line_separator()
        text += f'{prefix}{msg}{line_sep}'
        self.output_log.set_text(text)
