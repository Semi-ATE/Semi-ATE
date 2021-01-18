from transitions.extensions import HierarchicalMachine as Machine

from ATE.Tester.TES.apps.masterApp.statemachines.TestingSiteMachine import (TestingSiteModel, TestingSiteMachine)

from typing import List


class MultiSiteTestingMachine(Machine):

    def __init__(self, model=None):
        states = ['inprogress', 'waiting_for_resource', 'completed']
        super().__init__(model=model, states=states, initial='inprogress'),

        self.add_transition('all_sites_waiting_for_resource',       'inprogress',              'waiting_for_resource')      # noqa: E241
        self.add_transition('resource_config_applied',              'waiting_for_resource',    'inprogress')                # noqa: E241
        self.add_transition('all_sites_completed',                  '*',                       'completed')                 # noqa: E241


class MultiSiteTestingModel:
    def __init__(self, site_ids: List[str], parent_model=None):
        self._site_models = {site_id: TestingSiteModel(site_id) for site_id in site_ids}
        self._site_machines = {site_id: TestingSiteMachine(self._site_models[site_id]) for site_id in site_ids}
        self._parent_model = parent_model if parent_model is not None else self

    def handle_reset(self):
        for site in self._site_models.values():
            if site.is_completed():
                site.reset()

    def handle_resource_request(self, site_id: str, resource_request: dict):
        self._site_models[site_id].resource_requested(resource_request=resource_request)

        for site in self._site_models.values():
            if site.resource_request is not None and site.resource_request != resource_request:
                raise RuntimeError(f'mismatch in resource request from site "{site_id}": previous request of site "{site.site_id}" differs')

        self._check_for_all_remaing_sites_waiting_for_resource()

    def _on_resource_config_applied(self):
        if not self.is_waiting_for_resource():
            return  # ignore late callback if we already left the state

        self.resource_config_applied()
        for site in self._site_models.values():
            if site.is_waiting_for_resource():
                site.resource_ready()

    def handle_testresult(self, site_id: str, testresult: dict):
        self._site_models[site_id].testresult_received(testresult=testresult)
        if not self._check_for_all_sites_completed():
            self._check_for_all_remaing_sites_waiting_for_resource()

    def handle_status_idle(self, site_id: str):
        self._site_models[site_id].status_idle()
        if not self._check_for_all_sites_completed():
            self._check_for_all_remaing_sites_waiting_for_resource()

    def _check_for_all_sites_completed(self):
        if all(site.is_completed() for site in self._site_models.values()):
            self.all_sites_completed()
            self._parent_model.all_sitetests_complete()
            return True
        return False

    def _check_for_all_remaing_sites_waiting_for_resource(self):
        if self.is_waiting_for_resource():
            return  # already transitioned to state

        if any(site.is_inprogress() for site in self._site_models.values()):
            return  # at least one site is still busy

        sites_waiting = [site for site in self._site_models.values() if site.is_waiting_for_resource()]
        if not sites_waiting:
            return  # no site is waiting for resource

        self.all_sites_waiting_for_resource()
        resource_request = sites_waiting[0].resource_request  # all sites have same request
        self._parent_model.apply_resource_config(resource_request, lambda: self._on_resource_config_applied())  # Callable[[dict, Callable], None]

    def is_waiting_for_resource(self):
        # HACK: referencing the parent state by name sucks, but apparently we do not get
        # a monkey patched self.waiting_for_resource() to check if we are in 'our' nested state
        return self.state == 'testing_waiting_for_resource'
