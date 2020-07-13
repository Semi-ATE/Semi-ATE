# # -*- coding: utf-8 -*-
from ATE.spyder.widgets.sequencers import Harness
from ATE.spyder.widgets.sequencers.ExecutionPolicy import ExecutionPolicyABC
from ATE.spyder.widgets.sequencers.TestCase import TestCaseABC

# Nummerierung der Outparameter über alle Outputparameter


class SequencerBase:
    def __init__(self, test_settings):
        self.test_cases = []
        self.instance_counts = {}
        self.param_counts = 0
        self.test_settings = test_settings

        # ToDo: This might not be a good idea, as it
        # will cause silent fails, if the testprogram does
        # not set a harness
        self.harness = Harness.Harness()

    def __is_trigger_on_fail_enabled(self):
        return False

    def __is_trigger_on_test_enabled(self):
        return False

    def __get_trigger_on_test_index(self):
        return 0

    def __is_stop_on_fail_enabled(self):
        return False

    def __get_instance_count(self, test_class_name):
        if test_class_name not in self.instance_counts.keys():
            return 0
        return self.instance_counts[test_class_name]

    def __increase_instance_count(self, test_class_name):
        if test_class_name not in self.instance_counts.keys():
            self.instance_counts[test_class_name] = 0
        self.instance_counts[test_class_name] = (
            self.instance_counts[test_class_name] + 1
        )

    def register_test(self, test_instance):
        if test_instance is None:
            raise Exception("Cannot use none as a testcase.")

        if not issubclass(type(test_instance), TestCaseABC):
            raise Exception("A testcase must inherit from TestCaseABC")

        test_instance.set_instance_number(
            self.__get_instance_count(type(test_instance))
        )
        self.__increase_instance_count(type(test_instance))

        self.test_cases.append(test_instance)

    def set_harness(self, harness):
        """
        set_harness links this sequencer
        to a testharness.
        From this point on, the sequencer is
        ready to go.
        """
        if not issubclass(type(harness), Harness.Harness):
            raise Exception("Need harness type object")
        self.harness = harness
        # ToDo: If any exception occured previously
        #       we might want to set "ERROR" instead!
        self.harness.send_status("IDLE")

    def run(self, execution_policy, test_settings=None):
        if test_settings is not None:
            self.test_settings = test_settings
        if execution_policy is None:
            raise Exception("No Execution Policy set")
        if not issubclass(type(execution_policy), ExecutionPolicyABC):
            raise Exception("Need an execution policy type object")

        self.harness.send_status("TESTING")
        execution_policy.run(self)
        self.harness.send_status("IDLE")

    def after_test_cb(self, test_instance, test_index, test_result):
        """
        This function is called after the execution
        of each individual test by the execution policy
        """

        # Step 1: Check for failure
        failed = test_result[0]
        if failed:
            if self.__is_trigger_on_fail_enabled():
                pass  # ToDo

        # Check if the next test is our trigger_on_Test id
        # Note: This is not the perferct solution, as we can
        # never trigger on the first test.
        if self.__is_trigger_on_test_enabled():
            trigger_on_test_index = self.__get_trigger_on_test_index()
            if trigger_on_test_index == test_index + 1:
                pass  # ToDo: To Trigger

        # At last: publish testresults:
        self.harness.send_testresult(failed, test_result[1], test_result[2])

        if self.__is_stop_on_fail_enabled() and failed:
            return False
        return True

    def after_cycle_cb(self, cycle_index):
        """
        This function is called after the execution
        of a complete cylce of all tests the execution policy
        """
        pass
