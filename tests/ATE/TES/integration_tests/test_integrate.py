import pytest
import multiprocessing as mp

from ATE.Tester.TES.apps.launch_master import launch_master
from ATE.Tester.TES.apps.launch_control import launch_control
from ATE.Tester.TES.apps.launch_testapp import launch_testapp
from ATE.Tester.TES.apps.handlerApp.handler_runner import HandlerRunner
from tests.ATE.TES.integration_tests.DummySerial import DummySerialGeringer

import time
import asyncio
import aiohttp
import json
from util_timeout_ex import timeout_ex as timeout
import concurrent
from typing import Optional, List, Callable, Tuple, Union
import logging
import sys
import socket
import getpass
import aiomqtt
import paho.mqtt.client as mqtt
from contextlib import asynccontextmanager
import re
import itertools
import os
from hashlib import blake2b
from abc import ABC, abstractmethod
import xml.etree.ElementTree as tree

# pytestmark = pytest.mark.skip(reason='integration tests temporaroöy disabled for ci run')


LOGGER = logging.getLogger(__name__)
# LOGGER.addHandler(logging.StreamHandler())
# LOGGER.setLevel(logging.DEBUG)


XML_PATH = './tests/ATE/TES/apps/le306426001_template.xml'
XML_PATH_NEW = './tests/ATE/TES/apps/le306426001.xml'
TEST_PROGRAM = './tests/ATE/spyder/widgets/CI/qt/smoketest/smoke_test/src/HW0/PR/smoke_test_HW0_PR_Die1_Production_TheTest.py'
# TEST_PROGRAM = '.\\src\\ATE\\apps\\testApp\\thetest_application.py'


def generate_default_device_id():
    # goal: we don't want something fully random for debugging purposes,
    # but we want to avoid collissions when running multiple instances concurrently.
    # this hashes the file location, assuming concurrent runs will always use
    # different git repos.
    h = blake2b(digest_size=7)
    h.update(os.path.realpath(__file__).encode('utf-8'))
    loc_hash = h.hexdigest()
    return f'test_integrate_{socket.gethostname()}_{getpass.getuser()}_{loc_hash}'


# an env var van be used to configure a few things of the test env
# TODO: add a better way to configure the test environment (dedicated json file?)
ENVVAR_PREFIX = 'ATE_INTEGRATION_TESTENV_'

DEVICE_ID = os.getenv(ENVVAR_PREFIX + 'DEVICE_ID', generate_default_device_id())
HANDLER_ID = "HTO92-20F"

PIPELINE_ID = os.getenv("PIPELINE_ID", "1")
WEBPRT = str((int(PIPELINE_ID) % 4) + 8080)
WEBUI_PORT = os.getenv(ENVVAR_PREFIX + 'WEBUI_PORT', WEBPRT)
BROKER_HOST = os.getenv(ENVVAR_PREFIX + 'BROKER_HOST', '127.0.0.1')
BROKER_PORT = int(os.getenv(ENVVAR_PREFIX + 'BROKER_PORT', '1883'))

JOB_LOT_NUMBER = '306426.001'  # load ./tests/le306426001.xml


# this will generate the desired xml file and must be called before running the tests
def create_xml_file(device_id):
    if os.path.exists(XML_PATH_NEW):
        os.remove(XML_PATH_NEW)

    et = tree.parse(XML_PATH)
    root = et.getroot()
    for cl in root.findall("CLUSTER"):
        item = cl.find("TESTER1")
        if item is not None:
            item.text = device_id

    for st in root.findall("STATION"):
        item = st.find("STATION1")
        ts = item.find('TESTER1')
        ts.text = device_id

        pr = item.find('PROGRAM_DIR1')
        pr.text = TEST_PROGRAM

    et.write(XML_PATH_NEW)

# TODO: Implement a graceful shutdown for subprocesses (linux can simply use SIGTERM, a portable soluation for windows is a pita)
#       Note that this may be required in order to get reliable coverage results (which may be lost when a subprocess is killed before it can flush coverage reports)

# TODO: start a 'parent process watchdog' (see testapp) here as well to ensure we get rid of zombie processes when tests are cancelled? maybe we should do a killall all python processes from our virtualenv on CI as well.
#       alternatively or additionally add test/function that verifies via mqtt that all apps are dead (in order to fail if something is strange in our environment) ?
#       currently we can still end up with both, green and red, test results because of zombie processes still active in mqtt


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def handler_runner():
    configuration = {
        "handler_type": 'geringer',
        "handler_id": HANDLER_ID,
        "broker_host": BROKER_HOST,
        "broker_port": BROKER_PORT,
        "device_ids": [DEVICE_ID],
        "loglevel": 10
    }

    handler_runner = HandlerRunner(configuration, DummySerialGeringer())
    yield handler_runner
    await handler_runner.stop()


# executed in own process with multiprocessing, no references to testenv state
def run_master(device_id, sites, broker_host, broker_port, webui_port):
    create_xml_file(device_id)

    config = {
        "Handler": HANDLER_ID,
        'broker_host': broker_host,
        'broker_port': broker_port,
        'device_id': device_id,
        'sites': sites,
        'webui_port': webui_port,
        "skip_jobdata_verification": False,
        "webui_static_path": "./ATE/Tester/TES/ui/angular/mini-sct-gui/dist/mini-sct-gui",
        "filesystemdatasource.path": "./tests/ATE/TES/apps/",
        "filesystemdatasource.jobpattern": "le306426001.xml",
        "user_settings_filepath": "master_user_settings.json",
        "loglevel": 10
    }
    launch_master(config_file_path='ATE/Tester/TES/apps/master_config_file_template.json',
                  user_config_dict=config)


# executed in own process with multiprocessing, no references to testenv state
def run_control(device_id, site_id, broker_host, broker_port):
    config = {
        'broker_host': broker_host,
        'broker_port': broker_port,
        'device_id': device_id,
        'site_id': site_id
    }
    launch_control(config_file_path='ATE/Tester/TES/apps/control_config_file_template.json',
                   user_config_dict=config)


# executed in own process with multiprocessing, no references to testenv state
def run_testapp(device_id, site_id, broker_host, broker_port, thetestzipname):
    launch_testapp([
        'thetest_application.py',
        '--device_id', device_id,
        '--site_id', site_id,
        '--broker_host', broker_host,
        '--broker_port', str(broker_port),
        '--verbose',
        '--thetestzip_name', thetestzipname,
        '--file', 'external'
    ])


class ProcessManagerItem:
    proc_name: str
    process: mp.Process
    site_id: Optional[str]
    sites: Optional[List[str]]

    __slots__ = ["proc_name", "process", "site_id", "sites"]

    def __init__(self, proc_name, process, *, site_id=None, sites=None):
        self.proc_name = proc_name
        self.process = process
        self.site_id = site_id
        self.sites = sites

    def is_process_active(self):
        return self.process.exitcode is None


class ProcessManager:

    def __init__(self):
        self.processes = {}
        # important: use 'spawn' (default on windows) also on linux, because 'fork' does not work properly with asyncio.
        # details unknown, but asyncio will complain about loop already running in pytest when 'fork' is used to create
        # a process. this is apparently an open issue in python: https://bugs.python.org/issue22087
        self.mp_ctx = mp.get_context('spawn')

    def shutdown(self):
        self.kill_processes(*self.processes.keys())

    def start_master(self, proc_name, device_id, sites):
        self._assert_unused_name(proc_name)
        p = self.mp_ctx.Process(target=run_master,
                                args=(device_id, sites, BROKER_HOST, BROKER_PORT, WEBUI_PORT))
        self._add_process(proc_name, p)
        p.start()
        assert p.is_alive()
        return ProcessManagerItem(proc_name, p, sites=sites)

    def start_control(self, proc_name, device_id, site_id):
        self._assert_unused_name(proc_name)
        p = self.mp_ctx.Process(target=run_control,
                                args=(device_id, site_id, BROKER_HOST, BROKER_PORT))
        self._add_process(proc_name, p)
        p.start()
        assert p.is_alive()
        return ProcessManagerItem(proc_name, p, site_id=site_id)

    def start_testapp(self, proc_name, device_id, site_id):
        args = [str(sys.executable), os.path.basename(TEST_PROGRAM),
                '--device_id', device_id,
                '--site_id', site_id,
                '--broker_host', BROKER_HOST,
                '--broker_port', str(BROKER_PORT)]
        self._assert_unused_name(proc_name)
        import subprocess
        p = subprocess.Popen(args=args,
                             cwd=os.path.dirname(TEST_PROGRAM))
        # p = self.mp_ctx.Process(args=args)
        self._add_process(proc_name, p)
        return ProcessManagerItem(proc_name, p, site_id=site_id)

    def kill_process(self, proc_name: str):
        return self.kill_processes(proc_name)

    def kill_processes(self, *proc_names: str):
        if not proc_names:
            return

        ps = [self.processes[proc_name] for proc_name in proc_names]
        for proc_name in proc_names:
            del self.processes[proc_name]

        # could also use Process.sentinel with multiprocessing.connection.wait
        # to wait for multiple process exit, but using thread pool makes it
        # simpler to handle exceptions
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = list(executor.submit(self._kill_and_join_process, p)
                           for p in ps)
            concurrent.futures.wait(futures)
            # TODO: log some information about failures, maybe return two sets (done, fail)
            return any(f.exception() is None and f.result() is not None for f in futures)

    def _assert_unused_name(self, proc_name):
        if proc_name in self.processes:
            raise ValueError(f'process with name {proc_name} already exists')

    def _add_process(self, proc_name: str, p: mp.Process):
        self.processes[proc_name] = p

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.shutdown()

    def _kill_and_join_process(self, p: mp.Process):
        if p.exitcode is not None:
            return p.exitcode
        p.terminate()
        p.join(timeout=0.5)
        if p.exitcode is not None:
            return p.exitcode
        p.kill()
        p.join(timeout=0.5)
        return p.exitcode


@pytest.fixture
def process_manager():
    with ProcessManager() as instance:
        yield instance


@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
def test_master_startup(sites, process_manager):
    master = process_manager.start_master("master", DEVICE_ID, sites)
    assert master.proc_name == "master"
    assert master.process.exitcode is None
    time.sleep(2)
    assert master.process.exitcode is None


@pytest.mark.parametrize("sites", [['0']])
def test_control_startup(sites, process_manager):
    controls = [process_manager.start_control(f"control.{site_id}", DEVICE_ID, site_id)
                for site_id in sites]

    # processes are alive and data valid for 2 seconds
    for i in range(2):
        for control, site_id in zip(controls, sites):
            assert control.proc_name == f"control.{site_id}"
            assert control.site_id == site_id
            assert control.process.exitcode is None
            assert control.is_process_active()

        if i == 0:
            time.sleep(2)


def create_master(process_manager, sites):
    master = process_manager.start_master("master", DEVICE_ID, sites)
    return master


def create_controls(process_manager, sites):
    controls = [process_manager.start_control(f"control.{site_id}", DEVICE_ID, site_id)
                for site_id in sites]
    return controls


def create_standalone_testapp(process_manager, site_id):
    return process_manager.start_testapp(f"testapp.{site_id}", DEVICE_ID, site_id)


def create_sites(process_manager, sites):
    master = create_master(process_manager, sites)
    controls = create_controls(process_manager, sites)
    return master, controls


@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
def test_create_sites(sites, process_manager):
    master, controls = create_sites(process_manager, sites)

    # processes are alive and data valid for 2 seconds
    for i in range(2):
        assert master.proc_name == "master"
        assert master.sites == sites
        assert master.process.exitcode is None
        assert master.is_process_active()

        for control, site_id in zip(controls, sites):
            assert control.proc_name == f"control.{site_id}"
            assert control.site_id == site_id
            assert control.process.exitcode is None
            assert control.is_process_active()

        if i == 0:
            time.sleep(2)


@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
def test_create_and_kill_sites(sites, process_manager):
    master, controls = create_sites(process_manager, sites)

    # processes are alive and data valid for 2 seconds
    for i in range(2):
        assert master.proc_name == "master"
        assert master.sites == sites
        assert master.process.exitcode is None
        assert master.is_process_active()

        for control, site_id in zip(controls, sites):
            assert control.proc_name == f"control.{site_id}"
            assert control.site_id == site_id
            assert control.process.exitcode is None
            assert control.is_process_active()

        if i == 0:
            time.sleep(1)

    # kill all controls, one at a time
    for next_to_kill in range(len(sites)):
        assert [c.site_id for c in controls if c.is_process_active()] == sites[next_to_kill:]
        assert process_manager.kill_process(controls[next_to_kill].proc_name)
        assert [c.site_id for c in controls if c.is_process_active()] == sites[next_to_kill + 1:]
        time.sleep(1)

    # kill master
    assert master.is_process_active()
    assert process_manager.kill_process(master.proc_name)
    assert not master.is_process_active()


@pytest.fixture
async def with_websocket_retry():
    async with aiohttp.ClientSession() as session:
        for _ in range(3):
            try:
                async with session.ws_connect(f'http://127.0.0.1:{WEBUI_PORT}/ws') as ws:
                    yield ws
                    break
            except aiohttp.ClientError:
                await asyncio.sleep(1)
        yield None


@pytest.fixture
async def ws_connection():
    async with aiohttp.ClientSession() as session:
        def _ws_connect():
            return session.ws_connect(f'http://127.0.0.1:{WEBUI_PORT}/ws')
        yield _ws_connect


def parse_websocket_msg(msg):
    assert msg.type == aiohttp.WSMsgType.TEXT
    json_data = json.loads(msg.data)
    assert 'type' in json_data
    assert 'payload' in json_data
    return json_data


async def ws_message_reader(ws):
    async for msg in ws:
        yield parse_websocket_msg(msg)


async def read_ws_messages_until_state(ws, expected_state, timeout_secs=None):
    other_msgs = []
    all_states = []

    try:
        async with timeout(timeout_secs):
            async for json_msg in ws_message_reader(ws):
                if json_msg['type'] != 'status':
                    other_msgs.append(json_msg)
                    continue
                state = json_msg['payload']['state']
                all_states.append(state)
                if expected_state == state:
                    return True, all_states, other_msgs
    except asyncio.TimeoutError:
        return None, all_states, other_msgs

    return False, all_states, other_msgs


async def expect_message_with_state_ex(ws, expected_state, timeout_secs=30.0):
    result, all_states, other_msgs = await read_ws_messages_until_state(
        ws, expected_state, timeout_secs)
    assert result is not None  # timeout
    assert result is True      # ws closed
    return all_states, other_msgs


async def expect_message_with_state(ws, expected_state, timeout_secs=30.0):
    all_states, _ = await expect_message_with_state_ex(
        ws, expected_state, timeout_secs)
    return all_states


def remove_dups(iterable):
    # in python 3.7+ dict keys preserve insertion order!
    assert sys.version_info >= (3, 7)
    return list(dict.fromkeys(iterable))


def remove_adjacent_dups(iterable):
    return [k for k, _ in itertools.groupby(iterable)]


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
async def test_load_run_unload(sites, process_manager, ws_connection):
    master, controls = create_sites(process_manager, sites)
    # allow webservice to start up before attempting to connect ws
    await asyncio.sleep(1.0)

    async with ws_connection() as ws:

        # STEP 1: wait for initialized (all controls connected)
        seen_states = await expect_message_with_state(ws, 'initialized', 5.0)
        # if there was any state except initialized it must be connecting
        # (we cannot expect to actually see it though because the initial state may already be initialized)
        assert not (set(seen_states) - set(['connecting', 'initialized']))

        # STEP 2: load load
        await ws.send_json({'type': 'cmd', 'command': 'load', 'lot_number': f'{JOB_LOT_NUMBER}'})
        seen_states = await expect_message_with_state(ws, 'ready', 5.0)
        # TODO: this assertion is commented out, because we don't see 'loading' reliably as well.
        #       the reason is that state changes are only propagated every 1ms (and only if the main loop is unblocked)
        # assert remove_dups(seen_states) == ['loading', 'ready']
        assert not (set(seen_states) - {'loading', 'ready'})

        # STEP 3: run test
        await ws.send_json({'type': 'cmd', 'command': 'next'})
        # TODO: If 'tests' are finished too fast, we also don't seetesting (same as the problem with 'loading' above)
        #       Currently these tests rely on the fact that testing takes longer. This needs to be fixed.
        # TODO: Add an issue that short state changes are properly sent to the frontend (needs fix in master background task loop)
        await expect_message_with_state(ws, 'testing', 5.0)
        await expect_message_with_state(ws, 'ready', 10.0)
        # TODO: assert message with type=testresult is received. not sure if received before or after ready status message.

        # STEP 4: unload lot
        await ws.send_json({'type': 'cmd', 'command': 'unload'})
        seen_states = await expect_message_with_state(ws, 'initialized', 5.0)
        assert not (set(seen_states) - {'unloading', 'initialized'})

        # STEP 5: kill controls
        process_manager.kill_processes(*(c.proc_name for c in controls))
        await expect_message_with_state(ws, 'softerror', 5.0)


def create_mqtt_client():
    connected = asyncio.Event()
    message_queue = asyncio.Queue()

    def _on_connect(client, userdata, flags, rc):
        LOGGER.debug("mqtt callback: connect rc=%s", rc)

        if connected.is_set():
            pytest.fail(f'more than one call to mqtt callback _on_connect(rc={rc})')
        elif rc != 0:
            pytest.fail(f'mqtt connect failed _on_connect(rc={rc})')
        else:
            connected.set()

    def _on_disconnect(client, userdata, rc):
        LOGGER.debug('mqtt callback: disconnect rc=%s', rc)

        # note: any disconnection is unexpected and means test failure.
        # raising an exception here unfortunately does not allow us to
        # fail fast, because this callback is executed in a task that
        # is not created/awaited by us (see aiomqtt implementation)
        pytest.fail(f'unexpected call to mqtt callback _on_disconnect(rc={rc})')

    def _on_message(client, userdata, message: mqtt.MQTTMessage):
        LOGGER.debug(f'mqtt callback: message topic="{message.topic}"')

        message_queue.put_nowait(message)

    client = aiomqtt.Client()
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message
    return client, connected, message_queue


class MqttSession:
    def __init__(self, client, message_queue):
        self._client = client
        self.message_queue = message_queue

    def publish(self, topic, payload=None, qos=0, retain=False):
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        return self._client.publish(topic, payload, qos, retain)


# topic: string or tuple, see parameter of paho.mqtt.client.Client.subribe
# timeout (in seconds) is important, or this will block like forever.
# apparently paho mqtt does not use a reasonable connection timeout.
# it seems it does not even report inital connection failures at
# all (callbacks are not invoked).
@asynccontextmanager
async def mqtt_connection(host, port, topic=None, timeout=5):
    client, connected, message_queue = create_mqtt_client()

    if client.loop_start():
        raise RuntimeError('loop_start failed')

    try:
        client.connect_async(host, port)
        await asyncio.wait_for(connected.wait(), timeout=timeout)
        if topic is not None:
            client.subscribe(topic)
        yield MqttSession(client, message_queue)
    finally:
        await client.loop_stop()


async def util_delete_retained_messages(host, port, topic, timeout_secs=5.0):
    def _on_connect(client, userdata, flags, rc):
        client.subscribe(topic)

    def _on_message(client, userdata, message: mqtt.MQTTMessage):
        if message.retain:
            client.publish(message.topic, b'', qos=2, retain=True)

    client = aiomqtt.Client()
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.loop_start()
    client.connect_async(host, port)
    try:
        await asyncio.sleep(timeout_secs)
        client.disconnect()
        await asyncio.sleep(0.1)
    finally:
        await client.loop_stop()


# TODO HACK WORKAROUND: enable this test and subsequent tests will fail,
# because currently master does not publish initial state without
# active controls or retained messages of previous runs
@pytest.mark.skip(reason="HACK subsequent tests will fail without retained control status")
@pytest.mark.asyncio
async def test_delete_retained_messages():
    topic = (f'ate/{DEVICE_ID}/#', 2)

    await util_delete_retained_messages(BROKER_HOST, BROKER_PORT, topic)

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        # expect a non-retained message on the status topic
        with pytest.raises(asyncio.TimeoutError) as excinfo:
            async with timeout(5, "no-retained-message-received"):
                while True:
                    msg = await mqtt.message_queue.get()
                    assert not msg.retain
            assert "no-retained-message-received" in str(excinfo.value)


@pytest.mark.asyncio
async def test_master_publishes_on_status_topic_after_start(process_manager):
    topic = (f'ate/{DEVICE_ID}/Master/status', 2)

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        _ = process_manager.start_master("master", DEVICE_ID, ['0'])

        # expect a non-retained message on the status topic
        async with timeout(5, "expecting non-retained message on status topic"):
            while True:
                msg = await mqtt.message_queue.get()
                if not msg.retain:
                    break


class MqttBaseMessage(ABC):
    def __init__(self, topic: str, payload: dict, retain: bool):
        self.topic = topic
        self.payload = payload
        self.retain = retain

    @classmethod
    @abstractmethod
    def from_mqtt_message(cls, message: mqtt.MQTTMessage):
        pass

    @classmethod
    def is_topic_match(cls, topic):
        return False


class MqttStatusMessage(MqttBaseMessage):
    def __init__(self, device_id, component, site_id, state, topic: str, payload: dict, retain: bool):
        super().__init__(topic, payload, retain)
        self.device_id = device_id
        self.component = component
        self.site_id = site_id
        self.state = state

    @classmethod
    def from_mqtt_message(cls, message: mqtt.MQTTMessage):
        device_id, component, site_id = cls.try_parse_topic_parts(message.topic)
        assert device_id is not None
        assert component is not None
        # assert component == 'Master' or site_id is not None
        state, json_payload = cls.parse_status_payload(message.payload)
        return MqttStatusMessage(device_id, component, site_id, state,
                                 message.topic, json_payload, message.retain)

    @staticmethod
    def try_parse_topic_parts(topic):
        master_pattern = rf'ate/(.+?)/Master/status'
        m = re.match(master_pattern, topic)
        if m:
            return (m.group(1), 'Master', None)

        site_pattern = rf'ate/(.+?)/(Control|TestApp)/status/site(.+)$'
        m = re.match(site_pattern, topic)
        if m:
            return (m.group(1), m.group(2), m.group(3))

        master_pattern = rf'ate/(.+?)/Handler/status'
        m = re.match(master_pattern, topic)
        if m:
            return (m.group(1), 'Handler', None)

        return (None, None, None)

    @classmethod
    def is_topic_match(cls, topic):
        return cls.try_parse_topic_parts(topic)[0] is not None

    @staticmethod
    def parse_status_payload(payload):
        json_payload = json.loads(payload)
        assert 'type' in json_payload
        assert json_payload['type'] == 'status'
        return json_payload['payload']['state'], json_payload

    def __repr__(self):
        return f'<MqttStatusMessage(state="{self.state}")>'


class MqttTestresultMessage(MqttBaseMessage):
    def __init__(self, device_id, site_id, ispass, testdata, topic, payload: dict, retain):
        super().__init__(topic, payload, retain)
        self.device_id = device_id
        self.component = 'TestApp'
        self.site_id = site_id
        self.ispass = ispass
        self.testdata = testdata

    @classmethod
    def from_mqtt_message(cls, message: mqtt.MQTTMessage):
        device_id, site_id = cls.try_parse_topic_parts(message.topic)
        assert device_id is not None
        assert site_id is not None
        ispass, testdata, json_payload = cls.parse_testresult_payload(message.payload)
        return MqttTestresultMessage(device_id, site_id, ispass, testdata,
                                     message.topic, json_payload, message.retain)

    @staticmethod
    def parse_testresult_payload(payload):
        json_payload = json.loads(payload)
        assert 'type' in json_payload
        assert json_payload['type'] == 'testresult'
        assert 'payload' in json_payload
        return json_payload['type'], json_payload['payload'], json_payload

        # TODO: we have to do this differently
        # assert 'pass' in json_payload
        # assert 'testdata' in json_payload
        # return json_payload['pass'], json_payload['testdata'], json_payload

    @staticmethod
    def try_parse_topic_parts(topic):
        pattern = rf'ate/(.+?)/TestApp/testresult/site(.+)$'
        m = re.match(pattern, topic)
        if m:
            return (m.group(1), m.group(2))
        return (None, None)

    @classmethod
    def is_topic_match(cls, topic):
        return cls.try_parse_topic_parts(topic)[0] is not None

    def __repr__(self):
        return f'<MqttTestresultMessage(site_id="{self.site_id}")>'


class MqttResourceRequestMessage(MqttBaseMessage):
    def __init__(self, device_id, site_id, resource_id: str, config: dict, topic: str, payload: dict, retain: bool):
        super().__init__(topic, payload, retain)
        self.device_id = device_id
        self.component = 'TestApp'
        self.site_id = site_id
        self.resource_id = resource_id
        self.config = config

    @classmethod
    def from_mqtt_message(cls, message: mqtt.MQTTMessage):
        device_id, topic_resource_id, site_id = cls.try_parse_topic_parts(message.topic)
        assert device_id is not None
        assert site_id is not None
        payload_resource_id, config, json_payload = cls.parse_testresult_payload(message.payload)
        assert topic_resource_id == payload_resource_id
        return MqttResourceRequestMessage(device_id, site_id, payload_resource_id, config,
                                          message.topic, json_payload, message.retain)

    @staticmethod
    def parse_testresult_payload(payload):
        json_payload = json.loads(payload)
        assert 'type' in json_payload
        assert json_payload['type'] == 'resource-config-request'
        assert 'resource_id' in json_payload
        assert 'config' in json_payload
        return json_payload['resource_id'], json_payload['config'], json_payload

    @staticmethod
    def try_parse_topic_parts(topic) -> Union[Tuple[str, str, str], Tuple[None, None, None]]:
        pattern = rf'ate/(.+?)/TestApp/resource/(.+?)/site(.+)$'
        m = re.match(pattern, topic)
        if m:
            return (m.group(1), m.group(2), m.group(3))
        return (None, None, None)

    @classmethod
    def is_topic_match(cls, topic):
        return cls.try_parse_topic_parts(topic)[0] is not None

    def __repr__(self):
        return f'<MqttResourceRequestMessage(resource_id="{self.resource_id}, site_id="{self.site_id}")>'


class MqttMessageBuffer:
    def __init__(self, queue):
        self._buffer = []
        self._queue = queue

    async def read(self):
        while True:
            msg = await self.read_one()
            yield msg

    async def read_one(self):
        while True:
            inmsg = await self._queue.get()
            outmsg = self._filter_and_transform(inmsg)
            if outmsg is not None:
                self._buffer.append(outmsg)
                return outmsg

    async def read_all_for(self, duration_secs):
        new_messages = []
        async with timeout(duration_secs, suppress_exc=True):
            async for msg in self.read():
                new_messages.append(msg)
        return new_messages

    def clear(self):
        self._buffer.clear()

    async def discard(self):
        await asyncio.sleep(0)
        await self.read_all_for(0)
        self.clear()

    def _filter_and_transform(self, msg):
        return msg

    @property
    def messages(self):
        return self._buffer


class FilteredMqttMessageBuffer(MqttMessageBuffer):
    def __init__(self, queue, skip_retained=False, skip_unmatched=False):
        MqttMessageBuffer.__init__(self, queue)
        self.skip_retained = skip_retained
        self.skip_unmatched = skip_unmatched

    def _filter_and_transform(self, message: mqtt.MQTTMessage):
        if self.skip_retained and message.retain:
            return None
        converted = self._convert_message(message)
        if converted is not None or self.skip_unmatched:
            return converted
        return message

    def _convert_message(self, message: mqtt.MQTTMessage):
        converters = [MqttStatusMessage, MqttTestresultMessage, MqttResourceRequestMessage]
        for converter in converters:
            if converter.is_topic_match(message.topic):
                return converter.from_mqtt_message(message)
        return None


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
async def test_master_states_after_start_and_kill(sites, process_manager):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2)]

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        # start master and make sure it publishes 'connecting' (and only that)
        master = process_manager.start_master("master", DEVICE_ID, sites)

        async with timeout(5, 'waiting for state: "connecting"'):
            async for msg in buffer.read():
                assert msg.state == 'connecting'
                break

        # kill master and expect the last-will message (we allow another 'connecting' state before that)
        process_manager.kill_process(master.proc_name)

        async with timeout(5, 'waiting for state: "crash"'):
            async for msg in buffer.read():
                assert msg.state == 'connecting' or msg.state == 'crash'
                if msg.state == 'crash':
                    break

        await buffer.read_all_for(0)

        # final assertion over the full sequence of published states
        seen_state_changes = remove_adjacent_dups(msg.state for msg in buffer.messages)
        assert seen_state_changes == ['connecting', 'crash']


# This test uses fixed wait times and observes the environment longer than
# just the minimal duration.
@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
async def test_master_publishes_connecting_and_crash_states_slow(sites, process_manager):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2)]

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue)

        # before starting the master we expect to receive only retained retained messages
        initial_messages = await buffer.read_all_for(3)
        assert not [msg.state for msg in initial_messages if not msg.retain]

        # now start master and make sure it publishes 'connecting' (and only that)
        master = process_manager.start_master("master", DEVICE_ID, sites)

        messages_after_start = await buffer.read_all_for(3)
        seen_states_after_start = remove_adjacent_dups(msg.state for msg in messages_after_start if not msg.retain)
        assert seen_states_after_start == ['connecting']

        # kill master and expect the last-will message (we allow another 'connecting' state before that)
        process_manager.kill_process(master.proc_name)

        messages_after_kill = await buffer.read_all_for(3)
        seen_states_after_kill = remove_adjacent_dups(msg.state for msg in messages_after_kill if not msg.retain)
        assert seen_states_after_kill == ['crash'] or seen_states_after_kill == ['connecting', 'crash']


async def read_messages_until_state(
        buffer: MqttMessageBuffer,
        status_message_filter: Callable[[MqttStatusMessage], bool],
        expected_state, timeout_secs, valid_state_sequence=None):

    # fail fast if we see an invalid state, but allow optional states at the front.
    # note that this mainly exists to ignore repeated messages with the initial state.
    # we should use a real state machine to detect and validate arbitrary state sequences.
    first_valid_state_index = 0

    def check_valid_state(state):
        nonlocal first_valid_state_index
        if valid_state_sequence is None:
            return
        assert state in valid_state_sequence[first_valid_state_index:]
        first_valid_state_index = valid_state_sequence.index(state)

    messages = []
    async with timeout(timeout_secs, f'waiting for state: "{expected_state}"'):
        async for msg in buffer.read():
            messages.append(msg)
            if not isinstance(msg, MqttStatusMessage) or not status_message_filter(msg):
                continue
            check_valid_state(msg.state)
            if msg.state == expected_state:
                break
    return messages


async def read_messages_until_handler_state(buffer: MqttMessageBuffer, expected_state, timeout_secs, valid_state_sequence=None):
    return await read_messages_until_state(
        buffer, lambda msg: msg.component == 'Handler',
        expected_state, timeout_secs, valid_state_sequence)


async def read_messages_until_master_state(buffer: MqttMessageBuffer, expected_state, timeout_secs, valid_state_sequence=None):
    return await read_messages_until_state(
        buffer, lambda msg: msg.component == 'Master',
        expected_state, timeout_secs, valid_state_sequence)


async def read_messages_until_control_state(buffer: MqttMessageBuffer, site_id, expected_state, timeout_secs, valid_state_sequence=None):
    return await read_messages_until_state(
        buffer, lambda msg: msg.component == 'Control' and msg.site_id == site_id,
        expected_state, timeout_secs, valid_state_sequence)


async def read_messages_until_testapp_state(buffer: MqttMessageBuffer, site_id, expected_state, timeout_secs, valid_state_sequence=None):
    return await read_messages_until_state(
        buffer, lambda msg: msg.component == 'TestApp' and msg.site_id == site_id,
        expected_state, timeout_secs, valid_state_sequence)


async def read_messages_until_whatever(
        buffer: MqttMessageBuffer,
        timeout_secs: float,
        *predicates: Callable[[MqttBaseMessage], bool]) -> List[Union[MqttBaseMessage, mqtt.MQTTMessage]]:

    unmatched_predicates = list(predicates)

    messages = []
    async with timeout(timeout_secs, f'waiting for message until {len(unmatched_predicates)} predicates are satisifed'):
        async for msg in buffer.read():
            messages.append(msg)
            unmatched_predicates = [pred for pred in unmatched_predicates if isinstance(msg, MqttBaseMessage) and not pred(msg)]
            if not unmatched_predicates:
                break
    return messages


@pytest.mark.asyncio
async def test_handler_connecting_state(handler_runner):
    topic = [(f'ate/{HANDLER_ID}/Handler/status', 2)]

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        handler_runner.start()
        await asyncio.sleep(3.0)
        await read_messages_until_handler_state(buffer, 'connecting', 5.0, ['connecting'])


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [(['0'], 1)])
@pytest.mark.parametrize("handler", [DummySerialGeringer()])
async def test_handler_send_commands_to_load_next_and_unload(sites, handler, process_manager, handler_runner):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
             (f'ate/{HANDLER_ID}/Handler/status', 2)]

    # test the different handler implementation
    handler_runner.comm = handler
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        _ = create_master(process_manager, sites[0])
        _ = create_controls(process_manager, sites[0])
        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        handler_runner.start()
        await asyncio.sleep(3.0)
        await read_messages_until_handler_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        handler_runner.comm.put('load')
        await asyncio.sleep(3.0)
        await read_messages_until_master_state(buffer, 'ready', 5.0, ['loading', 'ready'])

        handler_runner.comm.put('next', site_num=sites[1])
        # to make sure that test execution is done
        await read_messages_until_master_state(buffer, 'ready', 10.0, ['testing', 'ready'])
        await asyncio.sleep(5.0)

        # TODO: analyse the problem with CI build, why this fail
        # handler_runner.comm.put('unload')
        # await asyncio.sleep(3.0)
        # await read_messages_until_master_state(buffer, 'initialized', 5.0, ['unloading', 'initialized'])


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [(['0'], 1)])
@pytest.mark.parametrize("handler", [DummySerialGeringer()])
async def test_handler_send_temperature(sites, handler, process_manager, handler_runner):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
             (f'ate/{HANDLER_ID}/Handler/status', 2),
             (f'ate/{HANDLER_ID}/Handler/response', 2)]

    # test the different handler implementation
    handler_runner.comm = handler
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        _ = create_master(process_manager, sites[0])
        _ = create_controls(process_manager, sites[0])
        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        handler_runner.start()
        await asyncio.sleep(3.0)
        await read_messages_until_handler_state(buffer, 'initialized', 10.0, ['connecting', 'initialized'])

        handler_runner.comm.put('temperature')
        await asyncio.sleep(3.0)
        async with timeout(10, 'waiting for "temperature" response message'):
            async for msg in buffer.read():
                message = json.loads(msg.payload)
                assert message['type'] == 'temperature'
                assert message['payload']['temperature'] == 169.5
                break


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", ['0'])
@pytest.mark.parametrize("handler", [DummySerialGeringer()])
async def test_handler_send_command_identify_to_master(sites, handler, process_manager, handler_runner):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
             (f'ate/{DEVICE_ID}/Master/response', 2),
             (f'ate/{HANDLER_ID}/Handler/status', 2)]

    # test the different handler implementation
    handler_runner.comm = handler
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        _ = create_master(process_manager, sites)
        _ = create_controls(process_manager, sites)
        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        handler_runner.start()
        await asyncio.sleep(3.0)
        await read_messages_until_handler_state(buffer, 'initialized', 10.0, ['connecting', 'initialized'])

        handler_runner.comm.put('identify')

        async with timeout(10, 'waiting for "identify" response message'):
            async for msg in buffer.read():
                message = json.loads(msg.payload)
                assert message['type'] == 'identify'
                assert message['payload']['name'] == DEVICE_ID
                break


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", ['0'])
@pytest.mark.parametrize("handler", [DummySerialGeringer()])
async def test_handler_send_command_getstate_to_master(sites, handler, process_manager, handler_runner):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
             (f'ate/{DEVICE_ID}/Master/response', 2),
             (f'ate/{HANDLER_ID}/Handler/status', 2)]

    # test the different handler implementation
    handler_runner.comm = handler
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        _ = create_master(process_manager, sites)
        _ = create_controls(process_manager, sites)
        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        handler_runner.start()
        await asyncio.sleep(3.0)
        handler_runner.comm.put('get-state')

        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['initialized'])


@pytest.mark.asyncio
@pytest.mark.parametrize("sites", [['0'], ['0', '1']])
async def test_master_states_during_load_and_unload(sites, process_manager, ws_connection):
    topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
             (f'ate/{DEVICE_ID}/TestApp/testresult/#', 2)]

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        # STEP 1a: Create master, wait for 'connecting'
        master = create_master(process_manager, sites)
        await read_messages_until_master_state(buffer, 'connecting', 5.0, ['connecting'])

        # STEP 1b: create controls, wait for initialized (all controls connected)
        _ = create_controls(process_manager, sites)
        await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

        async with ws_connection() as ws:
            await ws.send_json({'type': 'cmd', 'command': 'load', 'lot_number': f'{JOB_LOT_NUMBER}'})
            await read_messages_until_master_state(buffer, 'ready', 5.0, ['initialized', 'loading', 'ready'])

        async with ws_connection() as ws:
            await ws.send_json({'type': 'cmd', 'command': 'next'})
            msgs_while_testing = await read_messages_until_master_state(buffer, 'testing', 5.0, ['ready', 'testing'])
            msgs_while_testing += await read_messages_until_master_state(buffer, 'ready', 10.0, ['testing', 'ready'])

        async with ws_connection() as ws:
            await ws.send_json({'type': 'cmd', 'command': 'unload'})
            await read_messages_until_master_state(buffer, 'initialized', 5.0, ['ready', 'unloading', 'initialized'])

            process_manager.kill_processes(master.proc_name)
            await read_messages_until_master_state(buffer, 'crash', 5.0, ['initialized', 'crash'])

        # Final assertion of the overall state sequence
        all_seen_master_states = remove_adjacent_dups(
            [msg.state for msg in buffer.messages
             if isinstance(msg, MqttStatusMessage)])
        assert all_seen_master_states == [
            'connecting', 'initialized',
            'loading', 'ready',
            'testing', 'ready',
            'unloading', 'initialized',
            # 'connecting',  # STEP 5 commented out
            'crash']


@pytest.mark.asyncio
async def test_standalone_testapp_start_and_terminate(process_manager):
    subscriptions = [(f'ate/{DEVICE_ID}/TestApp/status/+', 2)]
    site_id = '0'

    # Note: The test app is usually only started by the control.
    #       In order to test the testapp independently we start the testapp
    #       manually, which should be close to what the control does, but it's
    #       not exactly the same.

    # simulate the control app, as it store the bin mapping in an environment variable
    os.environ['smoke_test_HW0_PR_Die1_Production_PR_1'] = "{'1': ['1'], '12': ['12', '13', '11'], '13': ['20'], '42': ['22'], '0': ['60000', '60001']}"
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, subscriptions) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        # STEP 1: create testapp, wait for 'idle' status
        testapp = create_standalone_testapp(process_manager, site_id)
        await read_messages_until_testapp_state(buffer, site_id, 'idle', 5.0, ['idle'])

        # STEP 2: send terminate command
        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'terminate', 'sites': [site_id]})
        await read_messages_until_testapp_state(buffer, site_id, 'terminated', 5.0, ['idle', 'terminated'])

        # STEP 3: check that testapp process is actually gone
        async with timeout(5, "waiting for testapp process to exit"):
            while testapp.process.returncode:
                await asyncio.sleep(0.25)

        # Final assertion of the overall state sequence
        all_seen_master_states = remove_adjacent_dups(
            [msg.state for msg in buffer.messages
             if isinstance(msg, MqttStatusMessage)])
        assert all_seen_master_states == ['idle', 'terminated']


# @pytest.mark.asyncio
# @pytest.mark.parametrize('num_dut_tests_to_run', [1, 5])
# @pytest.mark.parametrize('thetestzipname', ['sleepmock', 'example1'])
@pytest.mark.skip(reason="no way of currently testing this")
async def test_standalone_testapp_run_duttests(num_dut_tests_to_run, _, process_manager, ws_connection):
    subscriptions = [
        (f'ate/{DEVICE_ID}/TestApp/status/+', 2),
        (f'ate/{DEVICE_ID}/TestApp/testresult/+', 2)]
    site_id = '0'

    # Note: The test app is usually only started by the control.
    #       In order to test the testapp independently we start the testapp
    #       manually, which should be close to what the control does, but it's
    #       not exactly the same.

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, subscriptions) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        # STEP 1: create testapp, wait for 'idle' status
        testapp = create_standalone_testapp(process_manager, site_id)
        await read_messages_until_testapp_state(buffer, site_id, 'idle', 5.0, ['idle'])

        # STEP 2: run n duttests
        for _ in range(num_dut_tests_to_run):
            mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'next', 'sites': [site_id]})
            msgs_while_testing = await read_messages_until_testapp_state(buffer, site_id, 'testing', 5.0, ['idle', 'testing'])
            msgs_while_testing += await read_messages_until_testapp_state(buffer, site_id, 'idle', 5.0, ['testing', 'idle'])

            # collect messages a bit longer, since we cannot guarantee to see the message on testresult
            # topic before one on the status topic (or can we??)
            async with timeout(5, suppress_exc=True):
                while True:
                    testresult_msgs = [msg for msg in msgs_while_testing if isinstance(msg, MqttTestresultMessage)]
                    if testresult_msgs:
                        break
                    msgs_while_testing.append(await buffer.read_one())
            assert len(testresult_msgs) == 1

        # STEP 3: send terminate command
        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'terminate', 'sites': [site_id]})
        await read_messages_until_testapp_state(buffer, site_id, 'terminated', 5.0, ['idle', 'terminated'])

        # STEP 4: check that testapp process is actually gone
        async with timeout(5, "waiting for testapp process to exit"):
            while testapp.is_process_active():
                await asyncio.sleep(0.25)

        # Final assertion of the overall state sequence
        all_seen_testapp_states = remove_adjacent_dups(
            [msg.state for msg in buffer.messages
             if isinstance(msg, MqttStatusMessage)])
        expected_testapp_states = ['idle'] + num_dut_tests_to_run * ['testing', 'idle'] + ['terminated']
        assert all_seen_testapp_states == expected_testapp_states


@pytest.mark.asyncio
# @pytest.mark.skip(reason="no way of currently testing this")
async def test_standalone_testapp_test_process(process_manager):
    subscriptions = [
        (f'ate/{DEVICE_ID}/TestApp/status/+', 2),
        (f'ate/{DEVICE_ID}/TestApp/testresult/+', 2)]
    site_id = '0'
    os.environ['smoke_test_HW0_PR_Die1_Production_PR_1'] = "{'1': ['1'], '12': ['12', '13', '11'], '13': ['20'], '42': ['22'], '0': ['60000', '60001']}"
    async with mqtt_connection(BROKER_HOST, BROKER_PORT, subscriptions) as mqtt:
        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'terminate', 'sites': [site_id]})
        # STEP 1: create testapp, wait for 'idle' status
        _ = create_standalone_testapp(process_manager, site_id)
        await read_messages_until_testapp_state(buffer, site_id, 'idle', 5.0, ['idle'])

        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'next', 'sites': [site_id],
                                                      'job_data': {'sites_info': [{'siteid': f'{site_id}', 'partid': '1', 'binning': -1}]}})
        await read_messages_until_testapp_state(buffer, site_id, 'testing', 5.0, ['idle', 'testing'])

        await asyncio.sleep(5.0)

        # STEP 3: send terminate command
        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', {'type': 'cmd', 'command': 'terminate', 'sites': [site_id]})
        await read_messages_until_testapp_state(buffer, site_id, 'terminated', 5.0, ['idle', 'testing', 'terminated'])


# This test does not test the way the feature is intended. ToDo: Check ATE-82 against actual requiremens.
# @pytest.mark.asyncio
# @pytest.mark.parametrize("sites", [['0'], ['0', '1']])
# @pytest.mark.parametrize("testzipmockname", TESTZIPMOCKS)
# async def test_master_reset_if_error_occured(sites, testzipmockname, process_manager, ws_connection):
#     topic = [(f'ate/{DEVICE_ID}/Master/status', 2),
#              (f'ate/{DEVICE_ID}/TestApp/testresult/#', 2)]

#     async with mqtt_connection(BROKER_HOST, BROKER_PORT, topic) as mqtt:
#         buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

#         # Create master, wait for 'connecting'
#         _ = create_master(process_manager, sites)
#         await read_messages_until_master_state(buffer, 'connecting', 5.0, ['connecting'])

#         # create controls, wait for initialized (all controls connected)
#         control = create_controls(process_manager, sites)
#         await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])

#         async with ws_connection() as ws:

#             # load
#             await ws.send_json({'type': 'cmd', 'command': 'load', 'lot_number': f'{JOB_LOT_NUMBER}|{testzipmockname}'})
#             await read_messages_until_master_state(buffer, 'ready', 5.0, ['initialized', 'loading', 'ready'])

#             # kill control: since we can't provoke crash of testapp from here we just kill the controlapp
#             process_manager.kill_processes(*(c.proc_name for c in control))
#             await read_messages_until_master_state(buffer, 'softerror', 5.0, ['initialized', 'softerror'])

#             await asyncio.sleep(0.5)

#             # reset command from websocket
#             await ws.send_json({'type': 'cmd', 'command': 'reset'})
#             await read_messages_until_master_state(buffer, 'connecting', 5.0, ['softerror', 'connecting'])

#             # recreate control
#             control = create_controls(process_manager, sites)
#             await read_messages_until_master_state(buffer, 'initialized', 5.0, ['connecting', 'initialized'])


# @pytest.mark.asyncio
# @pytest.mark.parametrize('stop_on_fail_enabled', [True, False, None])  # None included for default (True)
@pytest.mark.skip(reason="no way of currently testing this")
async def test_standalone_testapp_stop_on_fail_setting(stop_on_fail_enabled, process_manager, ws_connection):
    subscriptions = [
        (f'ate/{DEVICE_ID}/TestApp/status/+', 2),
        (f'ate/{DEVICE_ID}/TestApp/testresult/+', 2),
        (f'ate/{DEVICE_ID}/TestApp/resource/#', 2)]
    site_id = '0'
    resource_id = 'myresourceid'
    expected_config = {'param': 'value'}

    # The following code will test if the user setting "duttest.stop_on_fail" is properly respected,
    # by using a test sequence with tests A, B, and C, where A passes, B fails and C will request a single resource.
    # * if "duttest.stop_on_fail" is enabled (default), the duttest will complete on its own.
    # * if "duttest.stop_on_fail" is disabled, test C will be executed.
    # Note that this test will not respond to the resource request, because we only want to test the option for now.
    # A full intergation test should check generated test results (most probably STDF records) and verify all tests
    # are executed and reported correctly.

    async with mqtt_connection(BROKER_HOST, BROKER_PORT, subscriptions) as mqtt:

        buffer = FilteredMqttMessageBuffer(mqtt.message_queue, skip_retained=True)

        # STEP 1: create testapp, wait for 'idle' status
        _ = create_standalone_testapp(process_manager, site_id)
        await read_messages_until_testapp_state(buffer, site_id, 'idle', 5.0, ['idle'])

        # STEP 2: run duttest
        next_cmd_payload = {'type': 'cmd', 'command': 'next', 'sites': [site_id]}
        if stop_on_fail_enabled is not None:
            next_cmd_payload.update({'job_data': {'stop_on_fail': {'active': stop_on_fail_enabled, 'value': -1}}})
        mqtt.publish(f'ate/{DEVICE_ID}/TestApp/cmd', next_cmd_payload)

        # CASE 2.1: with stop-on-fail enabled the duttests will execute and return test results immedately
        if stop_on_fail_enabled is not False:
            msgs_while_testing = await read_messages_until_whatever(
                buffer, 5.0,
                lambda msg: isinstance(msg, MqttStatusMessage) and msg.component == 'TestApp' and msg.site_id == site_id and msg.state == 'testing')

            msgs_while_testing += await read_messages_until_whatever(
                buffer, 5.0,
                lambda msg: isinstance(msg, MqttStatusMessage) and msg.component == 'TestApp' and msg.site_id == site_id and msg.state == 'idle',
                lambda msg: isinstance(msg, MqttTestresultMessage))

            test_result_msgs = [msg for msg in msgs_while_testing if isinstance(msg, MqttTestresultMessage)]
            assert len(test_result_msgs) == 1
            assert test_result_msgs[0].site_id == site_id
            assert not test_result_msgs[0].ispass

            resource_request_msgs = [msg for msg in msgs_while_testing if isinstance(msg, MqttResourceRequestMessage)]
            assert not resource_request_msgs

        # CASE 2.2: with stop-on-fail disabled tests cannot complete because the resource request will block until timeout
        else:
            msgs_while_testing = await read_messages_until_whatever(
                buffer, 5.0,
                lambda msg: isinstance(msg, MqttStatusMessage) and msg.component == 'TestApp' and msg.site_id == site_id and msg.state == 'testing',
                lambda msg: isinstance(msg, MqttResourceRequestMessage))

            resource_request_msgs = [msg for msg in msgs_while_testing if isinstance(msg, MqttResourceRequestMessage)]
            assert len(resource_request_msgs) == 1
            assert resource_request_msgs[0].site_id == site_id
            assert resource_request_msgs[0].resource_id == resource_id
            assert resource_request_msgs[0].config == expected_config

            test_result_msgs = [msg for msg in msgs_while_testing if isinstance(msg, MqttTestresultMessage)]
            assert not test_result_msgs

        # no cleanup required
