from transitions.extensions import HierarchicalMachine as Machine

from typing import Optional


class TestingSiteMachine(Machine):
    states = ['inprogress', 'waiting_for_resource', 'waiting_for_testresult', 'waiting_for_idle', 'completed', 'bininfoconfirmed']

    def __init__(self, model):
        super().__init__(model=model, states=self.states, initial='inprogress', send_event=True)

        self.add_transition('resource_requested',       'inprogress',                               'waiting_for_resource',     before='set_requested_resource')        # noqa: E241
        self.add_transition('resource_ready',           'waiting_for_resource',                     'inprogress',               before='clear_requested_resource')      # noqa: E241

        self.add_transition('testresult_received',      ['inprogress', 'waiting_for_resource'],     'waiting_for_idle',         before='set_testresult')                # noqa: E241
        self.add_transition('status_idle',              ['inprogress', 'waiting_for_resource'],     'waiting_for_testresult')                                           # noqa: E241

        self.add_transition('testresult_received',      'waiting_for_testresult',                   'completed',                before='set_testresult')                # noqa: E241
        self.add_transition('status_idle',              'waiting_for_idle',                         'completed')                                                        # noqa: E241

        self.add_transition('reset',                    'completed',                                'inprogress',               before='clear_testresult')              # noqa: E241
        self.add_transition('bininfo_received',         'inprogress',                               'bininfoconfirmed')                                                 # noqa: E241
        self.add_transition('reset',                    'bininfoconfirmed',                         'inprogress')                                                       # noqa: E241


class TestingSiteModel:
    site_id: str
    resource_request: Optional[dict]
    testresult: Optional[dict]

    def __init__(self, site_id: str):
        self.site_id = site_id
        self.resource_request = None
        self.testresult = None

    def set_requested_resource(self, event):
        self.resource_request = event.kwargs['resource_request']

    def clear_requested_resource(self, event):
        self.resource_request = None

    def set_testresult(self, event):
        self.testresult = event.kwargs['testresult']

    def clear_testresult(self, event):
        self.testresult = None
