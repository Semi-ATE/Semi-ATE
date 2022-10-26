# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: C. Jung

INFO:
    icons von https://github.com/spyder-ide/qtawesome
        conda install qtawesome

TODO:

"""
import os
import json
import time
from PyQt5 import QtCore


__author__ = "Zlin526F"
__copyright__ = "Copyright 2021, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = '0.0.6'


class Barprogress(QtCore.QThread):
    """Create a thread for timing controlled Progress Bar.

    Display testbenchname, each 0.5s the progress bar is incrementing.
    """
    reportProgress = QtCore.pyqtSignal(int)
    calculationFinished = QtCore.pyqtSignal()
    PROGRESSUPDATETIME = 0.2
    WATCHDOGTIME = 5

    def __init__(self, parent):
        """Initialise."""
        super().__init__()
        self.debug = parent.logger.debug
        self.progressbar = parent.gui.Progressbar_testbench
        self.reportProgress.connect(self.emitprogress)
        self.parent = parent
        self.testbenches_time = {}
        self.testbenches_time['last'] = None
        self.starttime = 0
        self.totaltime = 0

    def start(self, testbenchname):
        """Start the progressbar."""
        self.debug('Barprogress.start {}'.format(testbenchname))
        if self.testbenches_time['last'] is None:       # if None, than the first testbench starts
            self.starttime = time.time()
            totaltime = 0
            for i in self.testbenches_time:
                if self.testbenches_time[i] is not None:
                    totaltime += self.testbenches_time[i]
            self.totaltime = totaltime
        self.settestbenches_time(testbenchname)
        self.parent.gui.Ltestbench.setText(testbenchname)
        runtime = 2
        if testbenchname in self.testbenches_time:                  # is time always measured for this test?
            runtime = self.testbenches_time[testbenchname]
            self.progressbar.setFormat('%p%')
        else:
            self.progressbar.setFormat('Measure')
        tmp = round(runtime/self.PROGRESSUPDATETIME)
        maxprogressbar = tmp if tmp > 0 else 1
        self.progressbar.setMaximum(maxprogressbar)
        super().start()

    def stop(self):
        self.terminate()

    def settestbenches_time(self, testbench=None, ok=True):
        """Measure testbench running time, (only if breakpoint is not set!)

        if testbench== None than the test end catched,
        save the testbenche time to a file
        """
        last_testbench = self.testbenches_time['last']
        if ok and last_testbench is not None:
            self.testbenches_time[last_testbench] = round((time.time() - self.last_testbench_time), 3)
        if ok:
            self.testbenches_time['last'] = testbench
            self.last_testbench_time = time.time()
        else:
            self.testbenches_time['last'] = None
        self.debug('Barprogress.settestbenches_time : {}'.format(self.testbenches_time))

    def run(self) -> None:
        """Run the progressbar until terminate"""
        counter = 0
        while (True):
            if self.parent.gui.CBholdonbreak.isChecked() and (time.time()-self.parent.last_mqtt_time) > self.WATCHDOGTIME:
                self.reportProgress.emit(-1)
            else:
                counter += 1
                self.reportProgress.emit(counter)
            time.sleep(self.PROGRESSUPDATETIME)

    def emitprogress(self, value):
        """Display the new value to the progressbar."""
        if value == -1:
            self.parent.gui.Lelapsed.setStyleSheet("color: rgb(255, 0, 0)")
            self.parent.gui.Lelapsed.setText('Breakpoint ?')
            self.parent.gui.Lremain.setText('??'.format())
        else:
            self.progressbar.setValue(value)
            self.parent.gui.Lelapsed.setStyleSheet("color: rgb(255, 255, 255)")
            if self.starttime != 0:
                elapsedtime = time.time() - self.starttime
                remaintime = self.totaltime - elapsedtime
                if remaintime < 0:
                    remaintime = 0
                self.parent.gui.Lelapsed.setText('{} s'.format(round(elapsedtime, 3)))
                self.parent.gui.Lremain.setText('{} s'.format(round(remaintime, 3)))

    def finish(self, ok=None):
        """Display the finish message."""
        self.debug('Barprogress.finish {}'.format(ok))
        self.settestbenches_time(ok=ok)
        self.save_testbenches_time(ok)
        self.terminate()
        self.parent.gui.Lelapsed.setStyleSheet("color: rgb(255, 255, 255)")
        remain = '0.000 s'
        self.progressbar.setFormat('%p%')
        if ok is None:
            self.parent.gui.Ltestbench.setText('waiting....')
            remain = '?? s'
            self.progressbar.setValue(0)
        elif ok:
            self.parent.gui.Ltestbench.setText('done')
            self.progressbar.setValue(self.progressbar.maximum())
        else:
            # self.gui.Ltestbench.setText(self.gui.Ltestbench.text())     # 'Last: '
            self.progressbar.setValue(self.progressbar.maximum())
        self.parent.gui.Lremain.setText(remain)

    def clrProTime(self):
        self.testbenches_time = {}
        self.testbenches_time['last'] = None
        self.save_testbenches_time(True)

    def save_testbenches_time(self, save):
        if save and not self.parent.gui.CBholdonbreak.isChecked():
            try:
                with open(self.filename, 'w') as outfile:
                    json.dump(self.testbenches_time, outfile)
            except Exception:
                print("Coudn't write {self.filename}")
                pass

    def load_testbenches_time(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename, 'r') as infile:
                self.testbenches_time = json.load(infile)
        else:
            self.testbenches_time = {'last': None}
        self.debug('Barprogress.load_testbenches_time: {}'.format(self.testbenches_time))
