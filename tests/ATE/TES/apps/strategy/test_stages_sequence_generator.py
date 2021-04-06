import pytest
import os

from ATE.Tester.TES.apps.testApp.stages_sequence_generator.stages_sequence_generator import StagesSequenceGenerator


LAYOUT = [[0, 0], [1, 0]]
WRONG_LAYOUT = [[1, 1], [1, 0]]

ABS_PATH = os.path.join(os.path.dirname(__file__), 'dummy_execution_strategy.json')


class TestStagesSequenceGenerator:
    def setup_method(self, mocker):
        self.stages_generator = StagesSequenceGenerator(ABS_PATH)

    def teardown_method(self):
        self.stages_generator = None

    def test_generate_stages_sequence_with_correct_layout(self, mocker):
        assert self.stages_generator.get_execution_strategy(LAYOUT) == [[["0", "1"]], [["0"], ["1"]]]

    def test_generate_stages_sequence_with_wrong_layout(self):
        with pytest.raises(Exception):
            self.stages_generator.get_execution_strategy(WRONG_LAYOUT)
