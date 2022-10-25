"""Create an rotate cursor .


:Date: |today|
:Author: Christian Jung <jung@micronas.com>

"""

import sys
import time
import threading

__author__ = "Christian Jung"
__copyright__ = "Copyright 2021, TDK Micronas"
__credits__ = ["Christan Jung"]
__email__ = "christian.jung@micronas.com"


class spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in "|/-\\":
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write("\b")  # \b = backspace
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False
