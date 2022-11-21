# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)

"""ATE STIL (IEEE 1450) main widget."""

# Standard library imports
import os
import sys
import os.path as osp
from datetime import datetime
import logging
from typing import List, Optional, Union, Literal, Dict

# PEP 589 and 544 are available from Python 3.8 onwards
if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

# Third-party imports
import zmq
from qtpy.QtCore import Qt, Signal, QProcess, QSocketNotifier
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTreeWidgetItem

# Spyder imports
from spyder.utils.icon_manager import ima
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.widgets.tabs import Tabs
from spyder.widgets.simplecodeeditor import SimpleCodeEditor
from spyder.utils.programs import find_program

# Local imports
from ate_spyder_stil.api import STILActions
from ate_spyder.widgets.navigation import ProjectNavigation
from spyder.widgets.onecolumntree import OneColumnTree, OneColumnTreeActions


# Localization
_ = get_translation("spyder")

# Logging
logger = logging.getLogger(__name__)


class STILBasePayload(TypedDict):
    message: str


class STILErrWarnPayload(STILBasePayload):
    filename: str
    row: int
    col: int


class STILCompilerMsg(TypedDict):
    kind: Union[Literal['info'], Literal['error'], Literal['warning']]
    payload: Union[STILBasePayload, STILErrWarnPayload]


class CategoryItem(QTreeWidgetItem):
    """
    Category item for results.

    Notes
    -----
    Possible categories are Convention, Refactor, Warning and Error.
    """

    CATEGORIES = {
        "Warning": {
            'translation_string': _("Warning"),
            'icon': ima.icon("warning")
        },
        "Error": {
            'translation_string': _("Error"),
            'icon': ima.icon("error")
        }
    }

    def __init__(self, parent, category, number_of_messages=0):
        # Messages string to append to category.
        self.num_msgs = number_of_messages
        self.category = category
        title = self.gather_title()

        super().__init__(parent, [title], QTreeWidgetItem.Type)

        # Set icon
        icon = self.CATEGORIES[category]['icon']
        self.setIcon(0, icon)

    def increase_num_messages(self):
        self.num_msgs += 1

        title = self.gather_title()
        self.setText(0, title)

    def gather_title(self):
        if self.num_msgs > 1 or self.num_msgs == 0:
            messages = _('messages')
        else:
            messages = _('message')

        # Category title.
        title = self.CATEGORIES[self.category]['translation_string']
        title += f" ({self.num_msgs} {messages})"
        return title


class MessageItem(QTreeWidgetItem):
    def __init__(self, parent: QWidget, filename: str, msg:
                 str, row: int, col: int):
        super().__init__(parent, [msg], QTreeWidgetItem.Type)

        self.filename = filename
        self.row = row
        self.col = col


class STILTreeData(TypedDict):
    error: CategoryItem
    warning: CategoryItem
    node: QTreeWidgetItem


class STILTree(OneColumnTree):
    sig_edit_goto_requested = Signal(str, int, int)
    """
    This signal will request to open a file in a given row and column
    using a code editor.

    Parameters
    ----------
    path: str
        Path to file.
    line: int
        Cursor starting line position.
    column: int
        Cursor starting column position.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.results = None
        self.data: Dict[str, STILTreeData] = {}
        title = _("STIL compilation results")
        self.set_title(title)

    def activated(self, item: MessageItem):
        """Double-click event"""
        filename = item.filename
        row = item.row
        column = item.col
        self.sig_edit_goto_requested.emit(filename, row, column)

    def clicked(self, item):
        """Click event."""
        if (isinstance(item, CategoryItem) and
                not isinstance(item, MessageItem)):
            if item.isExpanded():
                self.collapseItem(item)
            else:
                self.expandItem(item)
        else:
            self.activated(item)

    def clear_results(self):
        self.clear()
        self.data = {}

    def add_file(self, filename):
        if filename not in self.data:
            file_node = QTreeWidgetItem(self, [filename], QTreeWidgetItem.Type)
            err_node = CategoryItem(file_node, 'Error')
            warn_node = CategoryItem(file_node, 'Warning')

            file_node.setIcon(0, ima.icon('GridFileIcon'))

            self.data[filename] = {
                'error': err_node,
                'warning': warn_node,
                'node': file_node
            }

    def append_file_msg(self, msg: STILCompilerMsg):
        kind = msg['kind']

        payload: STILErrWarnPayload
        payload = msg['payload']
        filename = payload['filename']
        msg = payload['message']
        row = payload['row']
        col = payload['col']

        self.add_file(filename)
        kind_node = self.data[filename][kind]
        file_node = self.data[filename]['node']
        kind_node.increase_num_messages()
        file_node.setExpanded(True)
        MessageItem(kind_node, filename, msg, row, col)


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

    sig_edit_goto_requested = Signal(str, int, int)
    """
    This signal will request to open a file in a given row and column
    using a code editor.

    Parameters
    ----------
    path: str
        Path to file.
    line: int
        Cursor starting line position.
    column: int
        Cursor starting column position.
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
        self.output_tree.sig_edit_goto_requested.connect(
            self.sig_edit_goto_requested)

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
        # stil file compilation shall only be triggered from the test flow
        # action we want to compile only the stil files required by a
        # specific test flow
        self.run_stil_action = self.create_action(
            STILActions.RunSTIL, _('STIL files Compilation Status'),
            self.create_icon('run_again'), triggered=lambda: ()
        )
        self.run_stil_action.setToolTip('STIL files Compilation Status: Idle')
        self.run_stil_action.setEnabled(False)

    def update_actions(self):
        pass

    def on_close(self):
        return super().on_close()

    # --- Private API
    # ------------------------------------------------------------------------
    def compile_stil(self, stil_files: Optional[List[str]] = None,
                     sig_to_chan_path: str = None):
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
        self.stil_process.finished.connect(self.stil_process_finished)

        # TODO: Determine STIL file location adequately
        project_path = self.project_info.project_directory
        cwd = project_path
        env = self.stil_process.processEnvironment()

        for var in os.environ:
            env.insert(var, os.environ[var])

        self.stil_process.setProcessEnvironment(env)
        self.stil_process.setWorkingDirectory(str(cwd))

        # Find STIL files recursively
        if stil_files is None:
            stil_files = []
            for root, _, files in os.walk(cwd.joinpath('pattern')):
                for file in files:
                    _, ext = osp.splitext(file)
                    ext = ext[1:]
                    if ext == 'stil' or ext == 'wav':
                        stil_files.append(osp.join(root, file))

        sscl_path = find_program('sscl')
        if sscl_path is None:
            err_msg = 'The STIL compiler (sscl) was not found in the system'
            self.publish_to_log(err_msg, level='ERROR')

            tree_msg = STILCompilerMsg(
                kind='error', payload=STILErrWarnPayload(
                    message=err_msg, filename='Global', row=0, col=0))
            self.output_tree.append_file_msg(tree_msg)
            return

        output_folder = str(cwd.joinpath('pattern_output'))
        args = ['sscl', '--port', str(self.stil_port), '-c', '-i']
        args += stil_files
        args += ['-m', sig_to_chan_path]
        args += ['-o', output_folder]

        self.stil_process.setProcessChannelMode(QProcess.SeparateChannels)
        self.stil_process.start(args[0], args[1:])
        self.stil_process_running = True

        self.run_stil_action.setToolTip(
            'STIL files Compilation Status: Running')
        self.run_stil_action.setEnabled(True)
        self.run_stil_action.setIcon(self.create_icon('stop'))

    def stil_process_finished(self, exit_code, exit_status):
        self.stil_process_running = False
        self.stil_process = None
        self.run_stil_action.setToolTip(
            'STIL files Compilation Status: Idle')
        self.run_stil_action.setEnabled(False)
        self.run_stil_action.setIcon(self.create_icon('run_again'))

    def on_stil_msg_received(self):
        try:
            response: STILCompilerMsg
            response = self.stil_sock.recv_json(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            return

        payload = response['payload']
        message = payload['message']
        if response['kind'] == 'info':
            logger.info(message)
            self.publish_to_log(message, level='INFO')
        else:
            self.publish_to_log(message, level=response['kind'].upper())
            self.tabwidget.setCurrentIndex(0)
            self.output_tree.append_file_msg(response)

    # --- Public API
    # ------------------------------------------------------------------------
    def set_project_information(
            self, project_info: Optional[ProjectNavigation]):
        self.project_info = project_info

    def notify_project_status(self, ate_project_loaded: bool):
        self.run_stil_action.setEnabled(False)

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
