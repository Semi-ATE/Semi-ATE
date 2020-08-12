from transitions import Machine

from ATE.apps.handlerApp.handler_connection_handler import ConnectionHandler
from handlerApp.handler_statemachine_component import States, Transitions


class HandlerApplication:
    def __init__(self, configuration: dict) -> None:
        self._connection_handler = ConnectionHandler(configuration)
        self.machine = Machine(model=self,
                               states=States.list(),
                               transitions=Transitions.list(),
                               initial='idle')

    def run(self) -> None:
        self._connection_handler.start_task()
