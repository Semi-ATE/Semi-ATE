# # -*- coding: utf-8 -*-
from ATE.sequencers.ExecutionPolicy import ExecutionPolicyABC
from ATE.sequencers.DutTestCaseABC import (DutTestCaseABC, DutTestCaseBase)
from ATE.sequencers.Utils import (generate_PIR_dict, generate_PRR_dict)
from ATE.sequencers.Result import Result

from ATE.sequencers.constants import Trigger_Out_Pulse_Width


class SequencerBase:
    def __init__(self):
        self.test_cases = []
        self.instance_counts = {}
        self.param_counts = 0
        self.test_settings = {}
        self.stdf_data = []
        self.tester_instance = None
        self.soft_bin = 0
        self.site_id = 0

    def set_site_id(self, site_id):
        self.site_id = site_id

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

    def set_tester_instance(self, tester_instance):
        self.tester_instance = tester_instance

    def run(self, execution_policy, test_settings={}):
        if test_settings:
            self.test_settings = test_settings
        if execution_policy is None:
            raise Exception("No Execution Policy set")
        if not issubclass(type(execution_policy), ExecutionPolicyABC):
            raise Exception("Need an execution policy type object")

        return execution_policy.run(self)

    def pre_cycle_cb(self):
        self.stdf_data = []
        self.soft_bin = 1
        self.stdf_data.append(generate_PIR_dict(head_num=0, site_num=int(self.site_id)))

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
        self.soft_bin = DutTestCaseBase._select_bin(self.soft_bin, test_result)

        if self.__is_stop_on_fail_enabled() and failed:
            return False

        return True

    def __is_trigger_on_fail_enabled(self):
        if "trigger_on_fail" in self.test_settings:
            return self.test_settings["trigger_on_fail"]["active"]
        else:
            return False

    def __is_stop_on_fail_enabled(self):
        if "stop_on_fail" in self.test_settings:
            return self.test_settings["stop_on_fail"]["active"]
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

        if not self.test_settings["trigger_on_test"]["active"]:
            return

        trigger_on_test_index = self.test_settings["trigger_on_test"]["value"]
        if trigger_on_test_index != test_index + 1:
            return

        if self.tester_instance is None:
            return

        self.tester_instance.pulse_trigger_out(Trigger_Out_Pulse_Width)

    def after_cycle_cb(self, execution_time, num_tests, test_result):
        """
        This function is called after the execution
        of a complete cylce of all tests the execution policy
        """
        # TODO: send request to get the hbin for the corresponding sbin
        # TODO: map correct field values instead of using hard codded values
        is_pass = test_result == Result.Pass()
        hard_bin = 11 if not is_pass else 1
        self.stdf_data.append(generate_PRR_dict(head_num=0, site_num=int(self.site_id), is_pass=is_pass,
                                                num_tests=num_tests, hard_bin=hard_bin, soft_bin=self.soft_bin,
                                                x_coord=1, y_coord=1, test_time=execution_time,
                                                part_id="1", part_txt="1", part_fix=[0b00000000]))

        return self.stdf_data

    def aggregate_tests_summary(self):
        tests_summary = []
        for test_case in self.test_cases:
            tests_summary += test_case.aggregate_tests_summary(head_num=0, site_num=int(self.site_id))

        return tests_summary
