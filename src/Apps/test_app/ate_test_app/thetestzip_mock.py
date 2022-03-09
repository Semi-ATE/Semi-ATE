import logging
import time
import itertools
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

import base64
from Semi_ATE.STDF import FAR, MIR, PIR, PTR, PRR, PCR, MRR, STDR

import contextlib


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TheTestZip_CallbackInterface(ABC):
    @abstractmethod
    def publish_stdf_part(self, stdf_blob: bytes):
        pass

    def request_resource_config(self, resource_id: str, config: dict):
        raise NotImplementedError


class TheTestZip_InstanceInterface(ABC):
    def setup(self):
        pass

    @abstractmethod
    def execute_dut_tests(self, job_param: dict) -> Tuple[bool, str]:
        pass

    def teardown(self):
        pass


class TheTestZip_TestFunc_ContextInterface(ABC):
    @abstractmethod
    def resource_context(self, resource_id: str, config: dict):
        pass

    @property
    @abstractmethod
    def job_param(self):
        pass


class TheTestZip_Mock_Null(TheTestZip_InstanceInterface):
    def execute_dut_tests(self, job_param: dict):
        return False, "<insert STDF data here>"


class TheTestZip_Mock_SleepMock(TheTestZip_InstanceInterface):

    def execute_dut_tests(self, job_param: dict):
        logger.info('executing mock test, sleeping for {mock_duration_secs}s...')
        time.sleep(float(job_param['mock_duration_secs']))
        test_result = job_param['mock_result']
        testdata = "AgAACgIETAABCr1VXl69VV5eACAgIP//IAYxMjM0NTYGTXlQYXJ0Bk15Tm9kZQhNeVRlc3RlcgVNeUpvYgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAUKAQEmAA8KAQAAAAEBQQAAAABAAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAA8KAgAAAAEBQAAAAEBAAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAUUAQEAAgABAP//AIAAgNEHAAAAAAAWAAEeAQEBAAAAAAAAAAAAAAABAAAA/////wcAARTBVV5eIAAA"
        logger.info('mock test sleep done, returning result: {test_result}')

        return test_result, testdata


# Note: placeholder only, eventually an individual part test func should probably return the PTR record itself (or another STDF record with all possible results)
class TheTestZip_PartTestResult:
    result_value: float

    def __init__(self):
        self.result_value = -9999.9


# record test statistics (to be put in STDF TSR, in case we actually add that)
# for now we simply record test name/id and exceution count
class TheTestZip_TestStatistics:
    def __init__(self):
        self.test_num_map = {}

    def record_test_execution(self, test_num, testname):
        prev_entry = self.test_num_map.get(test_num)
        if prev_entry is None:
            self.test_num_map[test_num] = {'testname': testname, 'exec_count': 0}
        elif testname != prev_entry['testname']:
            raise ValueError(f'test_num {test_num} reassigned to different name (was {prev_entry["testname"]}, now {testname})')
        self.test_num_map[test_num]['exec_count'] += 1


class TheTestZip_StdfProtocol:
    completed_part_records: List[List[STDR]]
    current_part_records: List[STDR]
    stats: TheTestZip_TestStatistics

    def __init__(self):
        self.version = 'V4'
        self.endian = '<'
        self.completed_part_records = []
        self.current_part_records = []
        self.stats = TheTestZip_TestStatistics()
        self.setup_timestamp = int(time.time())
        self.last_part_test_start_time = None

    def begin_part_test(self):
        if self.current_part_records:
            raise ValueError('begin already called')
        self.last_part_test_start_time = time.time_ns()
        self.current_part_records.append(self._create_PIR())

    def add_part_test_record(self, test_num: int, testname: str, result_ispass: bool, result_value: float):
        if not self.current_part_records:
            raise ValueError('begin not must be called first')

        self.stats.record_test_execution(test_num, testname)  # TODO: result_ispass
        self.current_part_records.append(self._create_PTR(test_num, result_ispass, result_value))

    def end_part_test(self, result_bin: int):
        if not self.current_part_records:
            raise ValueError('begin not must be called first')
        num_tests_executed = len(self.current_part_records) - 1  # don't include PIR
        test_duration_ms = (time.time_ns() - self.last_part_test_start_time) // 1000000  # time.time_ns() is python 3.7+
        self.current_part_records.append(self._create_PRR(num_tests_executed, result_bin, test_duration_ms))

        self.completed_part_records.append(self.current_part_records)
        self.current_part_records = []
        return self.completed_part_records[-1]

    def get_prolog(self):
        # FAR, MIR
        # optional (only have one site here): SDR
        return [self._create_FAR(), self._create_MIR()]

    def get_epilog(self):
        # optional (statistics): TSR, SBR
        # PCR, MRR
        num_parts_tested = len(self.completed_part_records)
        return [self._create_PCR(num_parts_tested), self._create_MRR()]

    def get_full_stdf_records(self):
        return self.get_prolog() + list(itertools.chain.from_iterable(self.completed_part_records)) + self.get_epilog()

    def _create_FAR(self):
        rec = FAR(self.version, self.endian)
        rec.set_value('CPU_TYPE', 2)
        rec.set_value('STDF_VER', 4)
        return rec

    def _create_MIR(self):
        rec = MIR(self.version, self.endian)

        rec.set_value('SETUP_T', self.setup_timestamp)
        rec.set_value('START_T', self.setup_timestamp)
        rec.set_value('STAT_NUM', 0)
        rec.set_value('LOT_ID', '123456')
        rec.set_value('PART_TYP', 'MyPart')
        rec.set_value('NODE_NAM', 'MyNode')
        rec.set_value('TSTR_TYP', 'MyTester')
        rec.set_value('JOB_NAM', 'MyJob')

        return rec

    def _create_PIR(self):
        rec = PIR(self.version, self.endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)
        return rec

    def _create_PTR(self, test_num: int, result_ispass: bool, result_value: float):
        rec = PTR(self.version, self.endian)

        rec.set_value('TEST_NUM', test_num)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)

        rec.set_value('TEST_FLG', 0b01000000 if result_ispass else 0b01000001)  # bit 1 set === 'RESULT' is valid, bit 7 set = test failed
        rec.set_value('PARM_FLG', 0)
        rec.set_value('RESULT', result_value)
        rec.set_value('TEST_TXT', '')
        rec.set_value('ALARM_ID', '')

        # TODO: workaround, need to explicitly set this or serialization raises exception
        rec.set_value('OPT_FLAG', 255)  # bit set means ignore some field

        # PTR is special in STDF, because all fields AFTER OPT_FLAG of the first PTR in the STDF file for a test defines the default values to be used for all following PTRs of the test
        # possibly not fully implemented here

        return rec

    def _create_PRR(self, num_tests_executed: int, bin: int, test_duration_ms: Optional[int] = None):
        rec = PRR(self.version, self.endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)

        rec.set_value('PART_FLG', 0)  # all bits 0 is ok and means part was tested and passed
        rec.set_value('NUM_TEST', num_tests_executed)
        rec.set_value('HARD_BIN', bin)

        if test_duration_ms is not None:
            rec.set_value('TEST_T', test_duration_ms)

        return rec

    def _create_PCR(self, num_parts_tested: int):
        rec = PCR(self.version, self.endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)

        # whats the difference between PART_CNT and FUNC_CNT?
        # is the following always true: RTST_CNT + ABRT_CNT + GOOD_CNT == PART_CNT == FUNC_CNT?
        rec.set_value('PART_CNT', num_parts_tested)
        rec.set_value('RTST_CNT', 0)
        rec.set_value('ABRT_CNT', 0)
        rec.set_value('GOOD_CNT', num_parts_tested)  # TODO: this is wrong, need to keep track of passes
        rec.set_value('PART_CNT', num_parts_tested)

        return rec

    def _create_MRR(self):
        rec = MRR(self.version, self.endian)

        rec.set_value('FINISH_T', int(time.time()))

        return rec

    @staticmethod
    def serialize_records(records) -> bytes:
        return bytes(itertools.chain.from_iterable(rec.__repr__() for rec in records))


# note: all mocked duttest_func return simplified results now (Tuple[bool, float], specifiying pass/fail and a result value).
# this means test are always executed, always have a valid result, there are no alarms etc.
# eventually we need to support the various cases of the STDF fields TEST_FLG, PARM_FLG etc and should probably allow individual tests to return the final PTR record (??)

def duttest_func_testnameA(testfunc_context) -> Tuple[bool, float]:
    time.sleep(1.0)
    return True, 1.0


def duttest_func_testnameB(testfunc_context) -> Tuple[bool, float]:
    # uncomment to allow attaching a debugger manually when this test is
    # note that ptvsd.enable_attach() must be called first, but this has to be done from the main thead on linux
    # see '--ptvsd-enable-attach' command line option option in thetest_application host app
    # import ptvsd
    # ptvsd.wait_for_attach()

    time.sleep(1.0)
    return False, 2.0


def duttest_func_testnameC(testfunc_context) -> Tuple[bool, float]:
    time.sleep(1.0)
    return True, 3.0


def duttest_func_testnameD(testfunc_context) -> Tuple[bool, float]:

    time.sleep(0.5)

    with testfunc_context.resource_context("myresourceid", {'param': 'value'}):
        time.sleep(0.25)

    time.sleep(0.25)

    return True, 4.0


# trivial sequence (passing)
duttest_sequence_example1 = [
    {'test_num': 1, 'testname': 'TESTNAME_A', 'testfunc': duttest_func_testnameA},
    {'test_num': 2, 'testname': 'TESTNAME_C', 'testfunc': duttest_func_testnameC},
]

# trivial sequence (failing, because first test fails)
duttest_sequence_example2 = [
    {'test_num': 1, 'testname': 'TESTNAME_B', 'testfunc': duttest_func_testnameB},
    {'test_num': 2, 'testname': 'TESTNAME_C', 'testfunc': duttest_func_testnameC},
]

# trivial sequence with resource synchronization
duttest_sequence_example3 = [
    {'test_num': 1, 'testname': 'TESTNAME_D', 'testfunc': duttest_func_testnameD},
]

# sequence with resource synchro after fail (different behavior depending on "stop-on-fail" option: resource synchro iff stop-on-fail is disabled)
duttest_sequence_example4 = [
    {'test_num': 1, 'testname': 'TESTNAME_A', 'testfunc': duttest_func_testnameA},
    {'test_num': 2, 'testname': 'TESTNAME_B', 'testfunc': duttest_func_testnameB},
    {'test_num': 3, 'testname': 'TESTNAME_D', 'testfunc': duttest_func_testnameD},
]


class TheTestZip_Mock_SimpleStdfRecord(TheTestZip_InstanceInterface):

    def execute_dut_tests(self, job_param: dict):
        rec = FAR('V4', '<')
        rec.set_value('CPU_TYPE', 2)
        rec.set_value('STDF_VER', 4)
        serialized_bytes = rec.__repr__()
        testdata = base64.b64encode(serialized_bytes).decode('utf-8')

        return True, testdata


class TheTestZip_TestFunc_ExampleContext(TheTestZip_TestFunc_ContextInterface):
    def __init__(self, resource_context, job_param):
        self._resource_context = resource_context
        self._job_param = job_param
        super().__init__()

    def resource_context(self, resource_id: str, config: dict):
        return self._resource_context(resource_id, config)

    def job_param(self):
        return self._job_param


def _generate_custom_sequence_entry(param_entry, implicit_test_num: int, current_site_id: str):
    test_num = param_entry.get('test_num', implicit_test_num)
    testname = param_entry.get('testname', f'duttest_mock_{test_num}')
    request_resource = param_entry.get('request_resource')
    if request_resource is not None:
        resource_id = param_entry.get('resource_id', 'myresourceid')
        resource_config = param_entry.get('config', {'param': 'value'})

    result_ispass = param_entry['result_ispass']  # result is required
    result_value = param_entry.get('result_value', float(test_num))
    duration_secs = param_entry.get('duration_secs', 0.5)

    # allow to specify different result and duration for individual sites sites
    site_overrides = param_entry.get('site_overrides', {}).get(current_site_id, {})
    result_ispass = site_overrides.get('result_ispass', result_ispass)
    result_value = site_overrides.get('result_value', duration_secs)
    duration_secs = site_overrides.get('duration_secs', duration_secs)

    def _duttest_func(testfunc_context) -> Tuple[bool, float]:
        if request_resource is not None:
            with testfunc_context.resource_context(resource_id, resource_config):
                time.sleep(duration_secs)
        else:
            time.sleep(duration_secs)

        return result_ispass, result_value

    return {
        'test_num': test_num,
        'testname': testname,
        'testfunc': _duttest_func
    }


def _generate_custom_sequence(job_param: dict):
    current_site_id = job_param['testzipmock.current_site_id']

    sequence: List[dict] = []
    params = job_param['testzipmock.custom_sequence']
    for param_entry in params:
        entry = _generate_custom_sequence_entry(param_entry, 1 + len(sequence), current_site_id)
        sequence.append(entry)

    return sequence


class TheTestZip_Mock_Example(TheTestZip_InstanceInterface):
    def __init__(self, sequence, callback_interface: TheTestZip_CallbackInterface):
        super().__init__()
        self.sequence = sequence
        self.protocol = TheTestZip_StdfProtocol()
        self.callback_interface = callback_interface

    def set_interface(self, callback_interface: TheTestZip_CallbackInterface):
        self.callback_interface = callback_interface

    def setup(self):
        logger.info('loading dut tests, sending initial stdf records')

        self.callback_interface.publish_stdf_part(
            self.protocol.serialize_records(self.protocol.get_prolog()))

    def execute_dut_tests(self, job_param: dict):
        logger.info('starting dut tests...')

        self.protocol.begin_part_test()
        result_overall_pass, result_bin = self._execute_dut_test_sequence(self.sequence, job_param)
        part_test_records = self.protocol.end_part_test(result_bin)

        logger.info('dut tests completed')

        stdf_part_blob = self.protocol.serialize_records(part_test_records)
        self.callback_interface.publish_stdf_part(stdf_part_blob)

        # also return string for json (full stdf for now, so we can more easily process it)
        # TODO: will we change the approach to always publish a full stdf as dut test result
        # (and remove the publishing from load/unload (respectively setup/teardown))?
        # TODO: stdf prolog contains info from all dut tests since load on purpose for now, but this is not meant to stay like this
        stdf_full_blob = (self.protocol.serialize_records(self.protocol.get_prolog())
                          + stdf_part_blob
                          + self.protocol.serialize_records(self.protocol.get_epilog()))
        testdata = base64.b64encode(stdf_full_blob).decode('utf-8')

        return result_overall_pass, testdata

    def teardown(self):
        logger.info('unloading dut tests, sending final stdf records')

        self.callback_interface.publish_stdf_part(
            self.protocol.serialize_records(self.protocol.get_epilog()))

        # with open("q:\\temp.stdf", "wb") as f:
        #     f.write(self.protocol.serialize_records(self.protocol.get_full_stdf_records()))

        self.protocol = TheTestZip_StdfProtocol()

    @contextlib.contextmanager
    def _resource_context(self, resource_id: str, config: dict):
        _ = self.callback_interface.request_resource_config(resource_id, config)
        yield
        # currently we always request the "default config" in order to
        # clean up, which is currently indicated by an empty dict.
        # this means we do not supported nested requests for different configs
        # TODO: do we need nested configs, i.e. restore the previously active config? if yes this needs to be implemented
        self.callback_interface.request_resource_config(resource_id, {})

    def _execute_dut_test_sequence(self, sequence, job_param: dict) -> Tuple[bool, int]:
        stop_on_fail = job_param.get('duttest.stop_on_fail', True)

        # Note: hbin and sbin make no difference for now: these will
        # eventually be remapped by other software components anyways
        # for now we simply use the test_num of the first failing test as final bin (or 0 if all pass)
        GOOD_BIN = 0
        WTF_BIN = 65535
        assert all(entry['test_num'] != GOOD_BIN for entry in sequence)

        result_bin = None
        entry = None
        for entry in sequence:
            testname = entry['testname']

            logger.info('excuting dut test: (%s) %s', entry['test_num'], testname)
            result_ispass, result_value = entry['testfunc'](TheTestZip_TestFunc_ExampleContext(self._resource_context, job_param))

            self.protocol.add_part_test_record(entry['test_num'], testname,
                                               result_ispass, result_value)
            if not result_ispass:
                if result_bin is None:
                    result_bin = entry['test_num']

                # unless stop_on_fail is explicitly deactivated, we stop testing as soon as a test fails
                if stop_on_fail:
                    # TODO: should we add records for the non-executed tests here?
                    break

        if entry is None:  # never executed any tests
            result_bin = WTF_BIN
        elif result_bin is None:  # at least one test executed and none failed
            result_bin = GOOD_BIN

        return result_bin == GOOD_BIN, result_bin


class TheTestZip_Mock_ExampleCustomSequence(TheTestZip_Mock_Example):
    def __init__(self, callback_interface: TheTestZip_CallbackInterface):
        super().__init__([], callback_interface)

    def execute_dut_tests(self, job_param: dict):
        self.sequence = _generate_custom_sequence(job_param)
        return super().execute_dut_tests(job_param)


def create_thetestzipmock_instance(thetestzip_name: str, callback_interface: TheTestZip_CallbackInterface) -> TheTestZip_InstanceInterface:
    if thetestzip_name == "null":
        return TheTestZip_Mock_Null()
    elif thetestzip_name == "sleepmock":
        return TheTestZip_Mock_SleepMock()
    elif thetestzip_name == "simplestdf":
        return TheTestZip_Mock_SimpleStdfRecord()
    if thetestzip_name == "example1":
        return TheTestZip_Mock_Example(duttest_sequence_example1, callback_interface)
    elif thetestzip_name == "example2":
        return TheTestZip_Mock_Example(duttest_sequence_example2, callback_interface)
    elif thetestzip_name == "example3":
        return TheTestZip_Mock_Example(duttest_sequence_example3, callback_interface)
    elif thetestzip_name == "example4":
        return TheTestZip_Mock_Example(duttest_sequence_example4, callback_interface)
    elif thetestzip_name == "custom":
        return TheTestZip_Mock_ExampleCustomSequence(callback_interface)
    else:
        raise RuntimeError(f'invalid testzip name "{thetestzip_name}", bye bye')
