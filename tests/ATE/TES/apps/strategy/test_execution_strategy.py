import pytest
import mock
import asyncio
from mock import call
from ATE.Tester.TES.apps.masterApp.execution_strategy.execution_strategy import DefaultExecutionStrategy

SITES = ['0', '1']
# key values ==>  site_num: execution_list
CONFIGURATION = [
                [['0'], ['1']],
                [['0', '1']]]

SITES_1 = ['0']


class DummyTester:
    def release_test_execution(self, sites: list):
        pass

    async def get_site_states(self, timeout: int):
        await asyncio.sleep(timeout)


class TestExecutionStrategy:
    def setup_method(self):
        self.strategy = DefaultExecutionStrategy(DummyTester())
        self.strategy.set_configuration(CONFIGURATION)

    def teardown_method(self):
        pass

    @mock.patch.object(DummyTester, 'release_test_execution')
    def test_release_test_execution_multi_times(self, mock):
        ret = self.strategy.handle_release(SITES)
        assert ret == ['0']
        assert self.strategy.test_num == 0

        ret = self.strategy.handle_release(SITES)
        assert ret == ['1']
        assert self.strategy.test_num == 0

        ret = self.strategy.handle_release(SITES)
        assert ret == ['0', '1']
        assert self.strategy.test_num == 1

        calls = [call(['0']), call(['1']), call(['0', '1'])]
        mock.assert_has_calls(calls)

        self.strategy.reset_stages()
        ret = self.strategy.handle_release(SITES)
        assert ret == ['0']
        assert self.strategy.test_num == 0

        ret = self.strategy.handle_release(SITES)
        assert ret == ['1']
        assert self.strategy.test_num == 0

    @mock.patch.object(DummyTester, 'release_test_execution')
    def test_release_test_execution_must_reset_before_starting_new_test_execution(self, mock):
        ret = self.strategy.handle_release(SITES)
        assert ret == ['0']
        assert self.strategy.test_num == 0

        ret = self.strategy.handle_release(SITES)
        assert ret == ['1']
        assert self.strategy.test_num == 0

        ret = self.strategy.handle_release(SITES)
        assert ret == ['0', '1']
        assert self.strategy.test_num == 1

        calls = [call(['0']), call(['1']), call(['0', '1'])]
        mock.assert_has_calls(calls)

        # 'reset_stage_execution_strategy' must be called, otherwise an exception
        # will be thrown
        with pytest.raises(Exception):
            _ = self.strategy.handle_release(SITES)

    @mock.patch.object(DummyTester, 'release_test_execution')
    def test_release_test_execution_reset_before_all_strategy_execute(self, mock):
        ret = self.strategy.handle_release(SITES)
        assert ret == ['0']
        assert self.strategy.test_num == 0

        # reset before execution of site '1' is handled
        with pytest.raises(Exception):
            self.strategy.reset_stages()

    def test_get_strategy_where_testing_sites_less_than_configured(self):
        ret = self.strategy.handle_release(SITES_1)
        assert ret == ['0']
        assert self.strategy.test_num == 0
        # remaining sites
        assert self.strategy.sites_to_release == []

        ret = self.strategy.handle_release(SITES_1)
        assert ret == ['0']
        assert self.strategy.test_num == 1
        # remaining sites
        assert self.strategy.sites_to_release == []

    def test_release_empty_sites_list_raises_exception(self):
        with pytest.raises(Exception):
            _ = self.strategy.handle_release([])

    def test_handle_release_before_configuration_is_set(self):
        # simulate empty strategy
        self.strategy.set_configuration([])

        with pytest.raises(Exception):
            _ = self.strategy.handle_release(SITES)

    @mock.patch.object(DummyTester, 'get_site_states')
    @pytest.mark.asyncio
    async def test_get_sites_states(self, mock):
        await self.strategy.get_site_states(0.1)
        mock.assert_called_once_with(0.1)
