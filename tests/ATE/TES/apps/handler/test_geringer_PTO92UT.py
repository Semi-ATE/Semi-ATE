import pytest
import mock
from ATE.Tester.TES.apps.handlerApp.handlers.geringer_PTO92UT import Geringer
from ATE.common.logger import Logger

# COMMMAND
LOAD_LOT_COMMAND =          'LL|306426.001|814A|120|237'
START_TEST_COMMAND =        'ST|02|1|12345|-01|002|000|1|12346|-01|002|000|154'
START_TEST_SITE_1_COMMAND = 'ST|02||12345|-01|002|000|1|12346|-01|002|000|105'
END_LOT_COMMAND =           'LE|013'
GET_NAME_COMMAND =          'ID?|072'
GET_MASTER_STATE_COMMAND =  'TS?|098'
GET_HANDLER_STATE_COMMAND = 'HS?|086'

TEMPERATURE_RESPONSE =      'TE|169.5|148'
STATUS_RESPONSE =           'HS|0|OK|217'
NAME_RESPONSE =             'ID|HTO92-17|112'

# RESPONSE
MASTER_NAME_RESPONSE =     'ID|SCT-81|005'
MASTER_STATE_RESPONSE =    'TS|0|OK|229'
MASTER_TEST_END_RESPONSE = 'ET|1|11112|111|111|111|097'   # TODO: impl. me other Story

MASTER_GET_STATE =          {'type': 'get-state', 'payload': {}}
MASTER_GET_NAME =           {'type': 'identify', 'payload': {}}

MASTER_STATE_RESPONSE_MQTT =   {'type': 'get-state', 'payload': {'state': 'ready', 'message': 'OK'}}
MASTER_NAME_RESPONSE_MQTT = {'type': 'identify', 'payload': {'name': 'SCT-81'}}
MASTER_TEST_END_RESPONSE_MQTT =  {'type': 'next', 'payload': {'sites': [{'siteid': '0', 'partid': '11112', 'binning': 111, 'logflag': 111, 'additionalinfo': 111}]}}


class DummySerial:
    def read(self):
        pass

    def write(self, message):
        pass

    def flush(self):
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
    assert message['type'] == 'load'
    assert message['payload'] == {'lot_number': '306426.001',
                                  'devicetype': '814A',
                                  'temperature': '120'}


def test_dispatch_start_test_message(geringer):
    message = geringer._dispatch_message(START_TEST_COMMAND)
    assert message['type'] == 'next'
    sites = [
        {'siteid': '0',
         'partid': '12345',
         'binning': -1,
         'logflag': 2,
         'additionalinfo': 0},
        {'siteid': '1',
         'partid': '12346',
         'binning': -1,
         'logflag': 2,
         'additionalinfo': 0}]

    assert message['payload'] == {'sites': sites}


def test_dispatch_start_test_only_site_1_message(geringer):
    message = geringer._dispatch_message(START_TEST_SITE_1_COMMAND)
    assert message['type'] == 'next'
    sites = [
        {'siteid': '1',
         'partid': '12346',
         'binning': -1,
         'logflag': 2,
         'additionalinfo': 0}]

    assert message['payload'] == {'sites': sites}


def test_dispatch_lot_end_message(geringer):
    message = geringer._dispatch_message(END_LOT_COMMAND)
    assert message['type'] == 'unload'
    assert message['payload'] == {}


def test_dispatch_get_test_name_message(geringer):
    message = geringer._dispatch_message(GET_NAME_COMMAND)
    assert message['type'] == 'identify'
    assert message['payload'] == {}


def test_dispatch_get_test_state_message(geringer):
    message = geringer._dispatch_message(GET_MASTER_STATE_COMMAND)
    assert message['type'] == 'get-state'
    assert message['payload'] == {}


def test_dispatch_temperature_response_message(geringer):
    message = geringer._dispatch_message(TEMPERATURE_RESPONSE)
    assert message['type'] == 'temperature'
    assert message['payload'] == {'temperature': 169.5}


def test_dispatch_name_response_message(geringer):
    message = geringer._dispatch_message(NAME_RESPONSE)
    assert message['type'] == 'identify'
    assert message['payload'] == {'name': 'HTO92-17'}


def test_dispatch_state_response_message(geringer):
    message = geringer._dispatch_message(STATUS_RESPONSE)
    assert message['type'] == 'state'
    assert message['payload'] == {'state': 0,
                                  'message': 'ok'}


@mock.patch.object(DummySerial, "write")
def test_handle_master_get_state_message(mock1, geringer):
    geringer.handle_message(MASTER_GET_STATE)
    DummySerial.write.assert_has_calls([mock.call(GET_HANDLER_STATE_COMMAND.encode('ASCII')), mock.call('\n'.encode('ASCII'))])


@mock.patch.object(DummySerial, "write")
def test_handle_master_get_name_message(mock1, geringer):
    geringer.handle_message(MASTER_GET_NAME)
    DummySerial.write.assert_has_calls([mock.call(GET_NAME_COMMAND.encode('ASCII')), mock.call('\n'.encode('ASCII'))])


@mock.patch.object(DummySerial, "write")
def test_handle_master_get_name_response_message(mock1, geringer):
    geringer.command.append('identify')
    geringer.handle_message(MASTER_NAME_RESPONSE_MQTT)
    DummySerial.write.assert_has_calls([mock.call(MASTER_NAME_RESPONSE.encode('ASCII')), mock.call('\n'.encode('ASCII'))])


@mock.patch.object(DummySerial, "write")
def test_handle_master_get_state_response_message(mock1, geringer):
    geringer.command.append('get-state')
    geringer.handle_message(MASTER_STATE_RESPONSE_MQTT)
    DummySerial.write.assert_has_calls([mock.call(MASTER_STATE_RESPONSE.encode('ASCII')), mock.call('\n'.encode('ASCII'))])


@mock.patch.object(DummySerial, "write")
def test_handle_master_test_end_response_message(mock1, geringer):
    geringer.command.append('next')
    geringer.handle_message(MASTER_TEST_END_RESPONSE_MQTT)
    DummySerial.write.assert_has_calls([mock.call(MASTER_TEST_END_RESPONSE.encode('ASCII')), mock.call('\n'.encode('ASCII'))])
