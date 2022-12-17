
"""ATE dispatcher producer and event listener subclasses."""

# Standard library imports
from typing import Any

# Qt imports
from qtpy.QtCore import Qt, Signal

# Third-party imports
from ate_dispatcher import Producer, ResultListener


class ATEProducer(Producer):
    def produce_dispatcher_output(self, topic: str, *args, **kwargs) -> Any:
        if topic == 'debug_ate':
            return 'print("Test response here")'


class ATEResultListener(ResultListener):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def process_dispatcher_result(self, topic: str, response: Any):
        self.parent.relay_dispatcher_result(response)
