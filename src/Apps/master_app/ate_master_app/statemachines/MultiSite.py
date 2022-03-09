from transitions.extensions import HierarchicalMachine as Machine

from ate_master_app.statemachines.TestingSiteMachine import (TestingSiteModel, TestingSiteMachine)

from typing import List


class MultiSiteTestingMachine(Machine):

    def __init__(self, model=None):
        states = ['inprogress', 'waiting_for_resource', 'completed', 'wating_for_release']
        super().__init__(model=model, states=states, initial='inprogress')

        self.add_transition('all_sites_waiting_for_resource',       '*',                                'waiting_for_resource')      # noqa: E241
        self.add_transition('resource_config_applied',              'waiting_for_resource',                      'inprogress')                # noqa: E241
        self.add_transition('all_sites_completed',                  '*',                                         'completed')                 # noqa: E241
        self.add_transition('all_sites_request_testing',            '*',                                         'inprogress')                # noqa: E241


class MultiSiteTestingModel:
    def __init__(self, site_ids: List[str], parent_model=None):
        self._site_models = {site_id: TestingSiteModel(site_id) for site_id in site_ids}
        self._site_machines = {site_id: TestingSiteMachine(self._site_models[site_id]) for site_id in site_ids}
        self._parent_model = parent_model if parent_model is not None else self

        self._site_test_result_received = {site_id: False for site_id in site_ids}
        self._released_sites = []

    def handle_reset(self):
        for site in self._site_models.values():
            if site.is_completed():
                site.reset()

        self.handle_reset_command()

    def handle_resource_request(self, site_id: str, resource_request: dict):
        self._site_models[site_id].resource_requested(resource_request=resource_request)

        for site in self._site_models.values():
            if site.resource_request is not None and site.resource_request != resource_request:
                raise RuntimeError(f'mismatch in resource request from site "{site_id}": previous request of site "{site.site_id}" differs')

        self._handle_resource_release()

    def _on_resource_config_applied(self):
        self.resource_config_applied()
        for site in self._site_models.values():
            if site.is_testing_waiting_for_resource():
                site.resource_ready()

    def _handle_resource_release(self):
        if not self._check_for_all_remaining_sites_waiting_for_resource():
            return

        resource_request = self._site_models[self._released_sites[0]].resource_request  # all sites have same request
        self._resource_required(resource_request)

    def handle_testresult(self, site_id: str, testresult: dict):
        self._site_test_result_received[site_id] = True

        self._site_models[site_id].testrequest_received()
        self._released_sites.pop(self._released_sites.index(site_id))
        self._handle_resource_release()

        if not self._check_for_all_sites_completed():
            return

        self.all_sites_completed()
        self._parent_model.all_sitetests_complete()
        self._reset_sites_result_received()

    def _reset_sites_result_received(self):
        for site_id in self._site_test_result_received:
            self._site_test_result_received[site_id] = False

    def handle_status_idle(self, site_id: str):
        # TODO: do we need this
        return

    def handle_sites_request(self, sites: List[int]):
        for site_id in range(len(sites)):
            site_id = str(site_id)
            if not self._site_models.get(str(site_id)):
                continue

            if self._site_models[site_id].is_testing_idle() and sites[int(site_id)]:
                self._site_models[site_id].testrequest_received()

            if self._site_models[site_id].is_testing_waiting_for_release() and not sites[int(site_id)]:
                self._site_models[site_id].testrequest_released()

            if self._site_models[site_id].is_testing_busy() and sites[int(site_id)]:
                self._site_models[site_id].testrequest_received()

        self.handle_test_request(str(site_id))

    def handle_test_request(self, site_id: str):
        if all(site.is_testing_waiting_for_release() for site in self._site_models.values()) and self.is_testing_inprogress():
            self.all_sites_request_testing()
            self._parent_model.all_site_request_testing()

    def handle_release(self, sites):
        self._released_sites = sites
        for site_id in sites:
            self._site_models[site_id].testrequest_released()

    def _check_for_all_sites_completed(self):
        return all(is_received for _, is_received in self._site_test_result_received.items())

    def _check_for_all_remaining_sites_waiting_for_resource(self):
        sites_waiting = [site_id for site_id, site in self._site_models.items() if site.is_testing_waiting_for_resource()]
        if set(sites_waiting) != set(self._released_sites) or not len(sites_waiting):
            return False

        return True

    def _resource_required(self, resource_request: dict):
        self.all_sites_waiting_for_resource()
        self._parent_model.apply_resource_config(resource_request, lambda: self._on_resource_config_applied())  # Callable[[dict, Callable], None]

    def handle_reset_command(self):
        for site in self._site_models.values():
            site.on_unload()

    def handle_execution_strategy_message(self, site_id: str, execution_strategy: List[List[List[str]]]):
        self._site_models[site_id].set_execution_strategy(execution_strategy)

        for site in self._site_models.values():
            if site.execution_strategy is not None and site.execution_strategy != execution_strategy:
                raise RuntimeError(f'mismatch in execution strategy configuration from site "{site_id}": "{execution_strategy}"\
                                   previous strategy configuration of site "{site.site_id}": "{site.execution_strategy}" differs')

        if (all([site.execution_strategy is not None for site in self._site_models.values()])):
            return True

        return False
