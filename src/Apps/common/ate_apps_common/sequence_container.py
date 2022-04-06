from ate_apps_common.transition_sequence import TransitionSequence
from typing import List, Callable


class SequenceContainer:
    def __init__(self, seq: List[str], site_ids: List[str], on_complete: Callable, on_error: Callable):
        self.sequences = {site_id: TransitionSequence(seq[:]) for site_id in site_ids}
        self.on_complete = on_complete
        self.on_error = on_error
        self.done = False

    def trigger_transition(self, site_id: str, transition: str, must_match_transition=True) -> bool:
        seq = self.sequences.get(site_id)
        if seq is None:
            self.on_error(site_id, transition)
            return False
        if not seq.trigger_transition(transition):
            if must_match_transition:
                self.on_error(site_id, transition)
            return False

        if all(x.finished() for x in self.sequences.values()):
            if self.done is False:
                self.on_complete()
                self.done = True

        return True
