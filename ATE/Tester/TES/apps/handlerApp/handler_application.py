class HandlerApplication:
    def __init__(self, machine):
        self._machine = machine

    def on_master_state_changed(self, state):
        print(state)

    def on_master_command_message(self, message):
        pass

    def on_master_response_message(self, message):
        pass

    def on_error_occured(self, error_message):
        self.on_error(error_message)

    def startup_done(self):
        self._machine.model.startup_done()

    @property
    def state(self):
        return self._machine.model.state
