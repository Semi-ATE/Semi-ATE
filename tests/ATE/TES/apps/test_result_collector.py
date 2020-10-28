from ATE.Tester.TES.apps.masterApp.resulthandling.result_collection_handler import ResultsCollector


def test_result_handler_without_setting_size():
    result_handler = ResultsCollector(0)
    assert not result_handler._get_size()


def test_store_data_and_get_all_stored_data():
    result_handler = ResultsCollector(3)
    result_handler.append(1)
    result_handler.append(2)

    assert len(result_handler.get_data()) == 2


def test_override_existing_data():
    result_handler = ResultsCollector(3)
    result_handler.append(1)
    result_handler.append(2)
    result_handler.append(3)
    result_handler.append(5)

    assert len(result_handler.get_data()) == 3
    assert result_handler.get_data()[2] == 5


def test_clear_available_data():
    result_handler = ResultsCollector(3)
    result_handler.append(1)
    result_handler.append(2)
    result_handler.append(3)

    result_handler.clear()

    assert len(result_handler.get_data()) == 0
