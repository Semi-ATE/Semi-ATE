from ATE.Tester.TES.apps.common.transition_sequence import TransitionSequence


class TestTransitionSequence:

    def test_empty_sequence_finished_yields_true(self):
        seq = TransitionSequence([])
        assert(seq.finished())

    def test_empty_sequnce_trigger_transition_yields_false(self):
        seq = TransitionSequence([])
        assert(not seq.trigger_transition("foo"))

    def test_trigger_transition_yields_true(self):
        seq = TransitionSequence(["foo", "bar"])
        assert(seq.trigger_transition("foo"))
        assert(not seq.finished())

    def test_trigger_transition_ignores_transition_to_same_state(self):
        seq = TransitionSequence(["foo", "bar"])
        # If we enter the same state twice in a row, this should
        # be ignored and not cause an error
        assert(seq.trigger_transition("foo"))
        assert(seq.trigger_transition("foo"))
        assert(not seq.finished())
