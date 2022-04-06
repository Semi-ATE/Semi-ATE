from transitions.extensions import HierarchicalMachine as Machine


class TestsExecutionMachine(Machine):
    states = ['idle', 'busy', 'terminate', 'waiting_for_release', 'waiting_for_resource', 'error']

    def __init__(self, model=None):
        super().__init__(model=model, states=self.states, initial='idle')

        # startup:
        self.add_transition(trigger='on_release',           source='idle',                  dest='waiting_for_release')      # noqa: E241
        self.add_transition(trigger='on_release',           source='waiting_for_release',   dest='busy')      # noqa: E241

        # request:
        self.add_transition(trigger='on_test_request',      source='busy',                  dest='waiting_for_release')   # noqa: E241
        self.add_transition(trigger='on_reqesut_release',   source='waiting_for_release',   dest='busy')         # noqa: E241

        # resource:
        self.add_transition(trigger='on_resource_request',  source='busy',                  dest='waiting_for_resource')          # noqa: E241
        self.add_transition(trigger='on_resource_ready',    source='waiting_for_resource',  dest='busy')    # noqa: E241

        # on error
        self.add_transition(trigger='on_error',             source='*',                     dest='error')          # noqa: E241
