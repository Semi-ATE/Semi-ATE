from typing import List
from abc import ABC, abstractmethod


def get_execution_strategy(strategy_type: str, tester: object):
    if 'simple' == strategy_type:
        return SimpleExecutionStrategy(tester)
    elif 'default' == strategy_type:
        return DefaultExecutionStrategy(tester)

    assert False, f"strategy with type: {strategy_type} is not supported"


class IExecutionStrategy(ABC):
    @abstractmethod
    def handle_release(self, sites: List[str]) -> List[str]:
        pass

    @abstractmethod
    def reset_stages(self):
        pass

    @abstractmethod
    def set_configuration(self, strategy_config: list):
        pass

    @abstractmethod
    async def get_site_states(self, timeout: int) -> List[int]:
        pass


class SimpleExecutionStrategy(IExecutionStrategy):
    def __init__(self, tester: object) -> None:
        self.tester = tester

    @staticmethod
    def handle_release(sites: List[str]) -> List[str]:
        return sites

    @staticmethod
    def reset_stages():
        pass

    @staticmethod
    def set_configuration(strategy_config: dict):
        pass

    async def get_site_states(self, timeout: int) -> List[int]:
        return await self.tester.get_site_states(timeout)


class DefaultExecutionStrategy:
    def __init__(self, tester: object):
        self._execution_strategy = {}
        self._stage_exectution_strategy = []
        self.tester = tester
        self._test_num = -1

    def handle_release(self, sites: List[str]) -> List[str]:
        if not len(sites):
            raise Exception('DefaultExecutionStrategy cannot release empty site list')

        sites_to_test = self.get_strategy_for_sites(sites)
        self.tester.release_test_execution(sites_to_test)
        return sites_to_test

    def get_strategy_for_sites(self, sites: List[str]) -> List[str]:
        if not self._stage_exectution_strategy:
            self._test_num += 1

            self._stage_exectution_strategy = self._get_testing_sites(sites)

        if not self._stage_exectution_strategy:
            raise Exception('DefaultExecutionStrategy cannot release empty site list')

        return self._stage_exectution_strategy.pop(0)

    def _get_testing_sites(self, sites: List[str]) -> List[str]:
        if self._test_num == -1:
            return []

        if not self._execution_strategy:
            raise Exception('execution strategy is not configured yet, no configuration is received')

        import copy
        stages = copy.deepcopy(self._execution_strategy[self.test_num])

        # all sites not contained in the list of sites that should test,
        # must be removed from the execution strategy
        for stage in stages:
            for index, site in enumerate(stage):
                if site in sites:
                    continue

                stage.pop(index)
                break

        # return all non empty list
        return [stage for stage in stages if len(stage)]

    async def get_site_states(self, timeout: int) -> List[int]:
        return await self.tester.get_site_states(timeout)

    def _is_valid_test_num(self, test_num: int) -> bool:
        return test_num in range(0, len(self._execution_strategy))

    def set_configuration(self, strategy_config: dict):
        self._execution_strategy = strategy_config

    @property
    def test_num(self) -> int:
        return self._test_num

    @property
    def sites_to_release(self) -> List[List[str]]:
        return self._stage_exectution_strategy

    def reset_stages(self):
        if len(self._stage_exectution_strategy):
            raise Exception(f'cannot reset execution_strategy, the following stages are not handled yet: {self._stage_exectution_strategy}')

        self._test_num = -1
