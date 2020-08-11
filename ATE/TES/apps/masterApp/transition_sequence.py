class TransitionSequence:
    def __init__(self, transitions: list):
        self.transitions = transitions[:]
        self.last_transition = ""

    def trigger_transition(self, transition: str) -> bool:
        if self.last_transition == transition:
            return True

        if self.finished():
            return False

        front_transition = self.transitions[0]
        if front_transition != transition:
            return False

        self.last_transition = self.transitions.pop(0)
        return True

    def finished(self):
        return len(self.transitions) == 0
