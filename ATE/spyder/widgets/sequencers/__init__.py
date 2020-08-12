# # -*- coding: utf-8 -*-
from ATE.spyder.widgets.sequencers import Harness
from ATE.spyder.widgets.sequencers.ExecutionPolicy import ExecutionPolicyABC
from ATE.spyder.widgets.sequencers.DutTestCaseABC import DutTestCaseABC
from ATE.spyder.widgets.sequencers.Utils import (generate_PIR, generate_PRR, generate_PTR, generate_TSR)
from ATE.spyder.widgets.sequencers.Result import Result

from ATE.spyder.widgets.sequencers.constants import Trigger_Out_Pulse_Width


class SequencerBase:
    def __init__(self, test_settings):
        self.test_cases = []
        self.instance_counts = {}
        self.param_counts = 0
        self.test_settings = test_settings
        self.stdf_data = []
        self.tester_instance = None
        self.soft_bin = 0

        # ToDo: This might not be a good idea, as it
        # will cause silent fails, if the testprogram does
        # not set a harness
        self.harness = Harness.Harness()

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

        if not issubclass(type(test_instance), DutTestCaseABC):
            raise Exception("A testcase must inherit from DutTestCaseABC")

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

    def set_tester_instance(self, tester_instance):
        self.tester_instance = tester_instance

    def run(self, execution_policy, test_settings=None):
        if test_settings is not None:
            self.test_settings = test_settings
        if execution_policy is None:
            raise Exception("No Execution Policy set")
        if not issubclass(type(execution_policy), ExecutionPolicyABC):
            raise Exception("Need an execution policy type object")

        execution_policy.run(self)

    def pre_cycle_cb(self):
        self.stdf_data = []
        self.soft_bin = 0
        self.harness.send_status("TESTING")
        self.stdf_data.append(generate_PIR(head_num=1, site_num=1))

    def after_test_cb(self, test_index, test_result):
        """
        This function is called after the execution
        of each individual test by the execution policy
        """

        # Step 1: Check for failure
        failed = test_result[0] == Result.Fail()
        self.do_trigger_on_fail(failed)
        self.do_trigger_on_test(test_index)

        result = test_result[2]
        self.stdf_data += result
        self.soft_bin = test_result[1]

        if self.__is_stop_on_fail_enabled() and failed:
            return False

        return True

    def __is_trigger_on_fail_enabled(self):
        if "trigger_on_fail" in self.test_settings:
            return self.test_settings["trigger_on_fail"]
        else:
            return False

    def __is_stop_on_fail_enabled(self):
        if "stop_on_fail" in self.test_settings:
            return self.test_settings["stop_on_fail"]
        return False

    def do_trigger_on_fail(self, failed):
        if not failed:
            return
        if not self.__is_trigger_on_fail_enabled():
            return

        self.tester_instance.pulse_trigger_out(Trigger_Out_Pulse_Width)

    def do_trigger_on_test(self, test_index):
        # Check if the next test is our trigger_on_Test id
        # Note: This is not the perferct solution, as we can
        # never trigger on the first test.
        if "trigger_on_test" not in self.test_settings:
            return

        trigger_on_test_index = self.test_settings["trigger_on_test"]
        if trigger_on_test_index != test_index + 1:
            return

        if self.tester_instance is None:
            return

        self.tester_instance.pulse_trigger_out(Trigger_Out_Pulse_Width)

    def after_cycle_cb(self, execution_time, num_tests):
        """
        This function is called after the execution
        of a complete cylce of all tests the execution policy
        """
        self.harness.send_status("IDLE")

        # TODO: send request to get the hbin for the corresponding sbin
        # TODO: map correct field values instead of using hard codded values
        self.stdf_data.append(generate_PRR(head_num=1, site_num=1, part_flag=0b00000000,
                                           num_tests=num_tests, hard_bin=1, soft_bin=self.soft_bin,
                                           x_coord=1, y_coord=1, test_time=execution_time,
                                           part_id="1", part_txt="1", part_fix=[0b00000000]))

        self.harness.send_testresult(self.stdf_data)

    def aggregate_tests_summary(self):
        tests_summary = []
        for test_case in self.test_cases:
            tests_summary += test_case.aggregate_tests_summary(head_num=1, site_num=1)

        self.harness.send_summary(tests_summary)
