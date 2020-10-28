from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.DutTestCaseABC import DutTestCaseBase


def test_select_bin_selects_other_bin_when_not_initialized():
    assert(1 == DutTestCaseBase._select_bin(-1, (Result.Pass(), 1)))


def test_select_bin_selects_lower_grade():
    assert(5 == DutTestCaseBase._select_bin(1, (Result.Pass(), 5)))


def test_select_bin_selects_fail_grade_for_pass_grade():
    assert(15 == DutTestCaseBase._select_bin(1, (Result.Pass(), 15)))


def test_select_bin_does_not_improve_grade():
    assert(5 == DutTestCaseBase._select_bin(5, (Result.Pass(), 1)))


def test_select_bin_does_not_change_fail_to_pass():
    assert(15 == DutTestCaseBase._select_bin(15, (Result.Pass(), 1)))


def test_select_bin_does_not_change_fail_to_other_fail():
    assert(15 == DutTestCaseBase._select_bin(15, (Result.Pass(), 21)))


def test_non_binning_result_does_not_change_bin():
    assert(15 == DutTestCaseBase._select_bin(15, (Result.Pass(), -1)))
    assert(1 == DutTestCaseBase._select_bin(1, (Result.Pass(), -1)))
    assert(0 == DutTestCaseBase._select_bin(0, (Result.Pass(), -1)))


def test_contact_fail_cannot_be_changed_to_pass_bin():
    assert(0 == DutTestCaseBase._select_bin(0, (Result.Pass(), 1)))


def test_contact_fail_cannot_be_changed_to_fail_bin():
    assert(0 == DutTestCaseBase._select_bin(0, (Result.Pass(), 55)))
