from transitions.extensions import HierarchicalMachine as Machine
from typing import List, Optional

from ate_master_app.statemachines.TestsExecutionMachine import TestsExecutionMachine


class TestingSiteMachine(Machine):
    states = ['inprogress',  # waiting
              'completed',
              'strategy_info_confirmed',
              {'name': 'testing', 'children': TestsExecutionMachine()},
              'error']

    def __init__(self, model):
        super().__init__(model=model, states=self.states, initial='testing', send_event=True)

        self.add_transition('testrequest_received',     'testing_idle',                             'testing_waiting_for_release'),                                              # noqa: E241
        self.add_transition('testrequest_received',     ['testing_busy', 'testing_waiting_for_resource'],             'testing_waiting_for_release'),                                              # noqa: E241
        self.add_transition('testrequest_released',     'testing_waiting_for_release',              'testing_busy'),                                                       # noqa: E241

        self.add_transition('resource_requested',       'testing_busy',                             'testing_waiting_for_resource',     before='set_requested_resource')        # noqa: E241
        self.add_transition('resource_ready',           'testing_waiting_for_resource',             'testing_busy',                     before='clear_requested_resource')      # noqa: E241

        self.add_transition('on_unload',                '*',                                        '=',                       after='clear_execution_strategy'),                             # noqa: E241

        self.add_transition('on_error',                 '*',                                        'error'),                                            # noqa: E241
        self.add_transition('reset',                    '*',                                        'inprogress',                       before=['clear_testresult', 'clear_execution_strategy']),              # noqa: E241


class TestingSiteModel:
    site_id: str
    resource_request: Optional[dict]
    testresult: Optional[dict]
    execution_strategy: Optional[List]

    def __init__(self, site_id: str):
        self.site_id = site_id
        self.resource_request = None
        self.testresult = None
        self.execution_strategy = None

    def set_requested_resource(self, event):
        self.resource_request = event.kwargs['resource_request']

    def clear_requested_resource(self, event):
        self.resource_request = None

    def set_testresult(self, event):
        self.testresult = event.kwargs['testresult']

    def clear_testresult(self, event):
        self.testresult = None

    def set_execution_strategy(self, strategy: List[List[str]]):
        self.execution_strategy = strategy

    def clear_execution_strategy(self, _):
        self.execution_strategy = None
