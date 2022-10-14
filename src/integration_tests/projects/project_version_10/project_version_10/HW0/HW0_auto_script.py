'''
This file is auto generated and is meant to be used to define user code which will be executed at the different stages of test program execution.

note: the file is generated only once, so any changes the user made will be presistent unless the file is manually deleted, in that case, editing the hardware again (or even open hwsetup wizard and save) will
generate the file again but with a default configuration.
'''

from ate_test_app.auto_script.AutoScriptBase import AutoScriptBase
from ate_common.logger import LogLevel

# logger and context are available, use as follow:
# self.logger
# self.context


class AutoScript(AutoScriptBase):
    def __init__(self):
        super().__init__()

    def before_start_setup(self):
        self.context.tester.setup()

    def after_cycle_teardown(self):
        pass

    def after_terminate_teardown(self):
        self.context.tester.teardown()

    def after_exception_teardown(self, source: str, exception: Exception):
        pass