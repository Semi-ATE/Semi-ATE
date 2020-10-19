import pytest
from ATE.Tester.TES.apps.handlerApp.handlers.geringer_PTO92UT import Geringer
from ATE.common.logger import Logger


LOAD_LOT_COMMAND =          'LL|306426.001|814A|120|237'
START_TEST_COMMAND =        'ST|02|1|12345|-01|002|000|1|12346|-01|002|000|154'
START_TEST_SITE_1_COMMAND = 'ST|02||12345|-01|002|000|1|12346|-01|002|000|105'
END_LOT_COMMAND =           'LE|013'
GET_TESTER_NAME_COMMAND =   'ID?|072'
GET_TEST_STATE_COMMAND =    'TS?|098'

TEMPERATURE_RESPONSE =      'TE|169.5|148'
STATUS_RESPONSE =           'HS|0|OK|217'
NAME_RESPONSE =             'ID|HTO92-17|112'


class DummySerial:
    def read():
        pass

    def write():
        pass


@pytest.fixture
def geringer():
    geringer = Geringer(DummySerial(), Logger('test'))
    return geringer


def test_dispatch_wrong_formed_message(geringer):
    assert not geringer._dispatch_message('')


def test_dispatch_wrong_formed_message_until_exception_fired(geringer):
    assert not geringer._dispatch_message('LL|SS|111')
    assert not geringer._dispatch_message('LL|SS|111')
    with pytest.raises(Exception):
        geringer._dispatch_message('LL|SS|111')


def test_dispatch_message_with_wrong_check_sum(geringer):
    assert not geringer._dispatch_message('LL|SS|111')
    assert geringer.error_count == 1


def test_dispatch_load_test_message(geringer):
    message = geringer._dispatch_message(LOAD_LOT_COMMAND)
    assert message['type'] == 'load_lot'
    assert message['payload'] == {'lotnumber': '306426.001',
                                  'devicetype': '814A',
                                  'temperature': '120'}


def test_dispatch_start_test_message(geringer):
    message = geringer._dispatch_message(START_TEST_COMMAND)
    assert message['type'] == 'next'
    sites = [
        {'siteid': 0,
         'deviceid': 12345,
         'binning': -1,
         'logflag': '002',
         'additionalinfo': 0},
        {'siteid': 1,
         'deviceid': 12346,
         'binning': -1,
         'logflag': '002',
         'additionalinfo': 0}]

    assert message['payload'] == {'sites': sites}


def test_dispatch_start_test_only_site_1_message(geringer):
    message = geringer._dispatch_message(START_TEST_SITE_1_COMMAND)
    assert message['type'] == 'next'
    sites = [
        {'siteid': 1,
         'deviceid': 12346,
         'binning': -1,
         'logflag': '002',
         'additionalinfo': 0}]

    assert message['payload'] == {'sites': sites}


def test_dispatch_lot_end_message(geringer):
    message = geringer._dispatch_message(END_LOT_COMMAND)
    assert message['type'] == 'terminate'
    assert message['payload'] == {}


def test_dispatch_get_test_name_message(geringer):
    message = geringer._dispatch_message(GET_TESTER_NAME_COMMAND)
    assert message['type'] == 'identify'
    assert message['payload'] == {}


def test_dispatch_get_test_state_message(geringer):
    message = geringer._dispatch_message(GET_TEST_STATE_COMMAND)
    assert message['type'] == 'get_state'
    assert message['payload'] == {}


def test_dispatch_temperature_response_message(geringer):
    message = geringer._dispatch_message(TEMPERATURE_RESPONSE)
    assert message['type'] == 'temperature'
    assert message['payload'] == {'temperature': 169.5}


def test_dispatch_name_response_message(geringer):
    message = geringer._dispatch_message(NAME_RESPONSE)
    assert message['type'] == 'name'
    assert message['payload'] == {'name': 'HTO92-17'}


def test_dispatch_state_response_message(geringer):
    message = geringer._dispatch_message(STATUS_RESPONSE)
    assert message['type'] == 'state'
    assert message['payload'] == {'state': 0,
                                  'message': 'ok'}
