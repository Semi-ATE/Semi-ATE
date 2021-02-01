#from ATE.data.STDF import (ATR, BPS, DTR, EPS, FAR, FTR, GDR, HBR,
#                                   MIR, MPR, MRR, PCR, PGR, PIR, PLR, PMR,
#                                   PRR, PTR, RDR, SBR, SDR, TSR, WCR, WIR,
#                                   WRR, get_STDF_setup_from_file, records_from_file)

from ATE.data.STDF.ATR import ATR
from ATE.data.STDF.BPS import BPS
from ATE.data.STDF.EPS import EPS
from ATE.data.STDF.FAR import FAR
from ATE.data.STDF.FTR import FTR
from ATE.data.STDF.GDR import GDR
from ATE.data.STDF.HBR import HBR
from ATE.data.STDF.MIR import MIR
from ATE.data.STDF.MPR import MPR
from ATE.data.STDF.MRR import MRR
from ATE.data.STDF.PCR import PCR
from ATE.data.STDF.PGR import PGR
from ATE.data.STDF.PIR import PIR
from ATE.data.STDF.PLR import PLR
from ATE.data.STDF.PMR import PMR
from ATE.data.STDF.PRR import PRR
from ATE.data.STDF.PTR import PTR
from ATE.data.STDF.RDR import RDR
from ATE.data.STDF.SBR import SBR
from ATE.data.STDF.SDR import SDR
from ATE.data.STDF.TSR import TSR
from ATE.data.STDF.WCR import WCR
from ATE.data.STDF.WIR import WIR
from ATE.data.STDF.WRR import WRR
from ATE.data.STDF.DTR import DTR
from ATE.data.STDF.STDR import get_STDF_setup_from_file
from ATE.data.STDF.STDR import ts_to_id
from ATE.data.STDF.STDR import supported


import struct
import pytest
from hypothesis import given, strategies as st
import itertools

import time
import sys
import io

class records_from_file(object):
    '''
    Generator class to run over the records in FileName.
    The return values are 4-fold : REC_LEN, REC_TYP, REC_SUB and REC
    REC is the complete record (including REC_LEN, REC_TYP & REC_SUB)
    if unpack indicates if REC is to be the raw record or the unpacked object.
    of_interest can be a list of records to return. By default of_interest is void
    meaning all records (of FileName's STDF Version) are used.
    '''
    debug = False

    def __init__(self, FileName, unpack=False, of_interest=None):
        if self.debug: print("initializing 'records_from_file")
        if isinstance(FileName, str):
            self.keep_open = False
            if not os.path.exists(FileName):
                raise STDFError("'%s' does not exist")
            self.endian = get_STDF_setup_from_file(FileName)[0]
            self.version = 'V%s' % struct.unpack('B', get_bytes_from_file(FileName, 5, 1))
            self.fd = open(FileName, 'rb')
        elif isinstance(FileName, io.IOBase):
            self.keep_open = True
            self.fd = FileName
            ptr = self.fd.tell()
            self.fd.seek(4)
            buff = self.fd.read(2)
            CPU_TYPE, STDF_VER = struct.unpack('BB', buff)
            if CPU_TYPE == 1: self.endian = '>'
            elif CPU_TYPE == 2: self.endian = '<'
            else: self.endian = '?'
            self.version = 'V%s' % STDF_VER
            self.fd.seek(ptr)
        else:
            raise STDFError("'%s' is not a string or an open file descriptor")
        self.unpack = unpack
        self.fmt = '%sHBB' % self.endian
        TS2ID = ts_to_id(self.version)
        if of_interest==None:
            self.records_of_interest = TS2ID
        elif isinstance(of_interest, list):
            ID2TS = id_to_ts(self.version)
            tmp_list = []
            for item in of_interest:
                if isinstance(item, str):
                    if item in ID2TS:
                        if ID2TS[item] not in tmp_list:
                            tmp_list.append(ID2TS[item])
                elif isinstance(item, tuple) and len(item)==2:
                    if item in TS2ID:
                        if item not in tmp_list:
                            tmp_list.append(item)
            self.records_of_interest = tmp_list
        else:
            raise STDFError("objects_from_file(%s, %s) : Unsupported of_interest" % (FileName, of_interest))
    def __del__(self):
        if not self.keep_open:
            self.fd.close()

    def __iter__(self):
        return self

    def __next__(self):
        while self.fd!=None:
            header = self.fd.read(4)
            if len(header)!=4:
                raise StopIteration
            else:
                REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.fmt, header)
                footer = self.fd.read(REC_LEN)
                if (REC_TYP, REC_SUB) in self.records_of_interest:
                    if len(footer)!=REC_LEN:
                        raise StopIteration()
                    else:
                        if self.unpack:
                            return REC_LEN, REC_TYP, REC_SUB, create_record_object(self.version, self.endian, (REC_TYP, REC_SUB), header+footer)
                        else:
                            return REC_LEN, REC_TYP, REC_SUB, header+footer


def create_record_object(Version, Endian, REC_ID, REC=None):
    '''
    This function will create and return the appropriate Object for REC
    based on REC_ID. REC_ID can be a 2-element tuple or a string.
    If REC is not None, then the record will also be unpacked.
    '''
    retval = None
    REC_TYP=-1
    REC_SUB=-1
    if Version not in supported().versions():
        raise STDFError("Unsupported STDF Version : %s" % Version)
    if Endian not in ['<', '>']:
        raise STDFError("Unsupported Endian : '%s'" % Endian)
    if isinstance(REC_ID, tuple) and len(REC_ID)==2:
        TS2ID = ts_to_id(Version)
        if (REC_ID[0], REC_ID[1]) in TS2ID:
            REC_TYP = REC_ID[0]
            REC_SUB = REC_ID[1]
            REC_ID = TS2ID[(REC_TYP, REC_SUB)]
    elif isinstance(REC_ID, str):
        ID2TS = id_to_ts(Version)
        if REC_ID in ID2TS:
            (REC_TYP, REC_SUB) = ID2TS[REC_ID]
    else:
        raise STDFError("Unsupported REC_ID : %s" % REC_ID)

    if REC_TYP!=-1 and REC_SUB!=-1:
        if REC_ID == 'PTR': retval = PTR(Version, Endian, REC)
        elif REC_ID == 'FTR': retval = FTR(Version, Endian, REC)
        elif REC_ID == 'MPR': retval = MPR(Version, Endian, REC)
        elif REC_ID == 'STR': retval = STR(Version, Endian, REC)
        elif REC_ID == 'MTR': retval = MTR(Version, Endian, REC)
        elif REC_ID == 'PIR': retval = PIR(Version, Endian, REC)
        elif REC_ID == 'PRR': retval = PRR(Version, Endian, REC)
        elif REC_ID == 'FAR': retval = FAR(Version, Endian, REC)
        elif REC_ID == 'ATR': retval = ATR(Version, Endian, REC)
        elif REC_ID == 'VUR': retval = VUR(Version, Endian, REC)
        elif REC_ID == 'MIR': retval = MIR(Version, Endian, REC)
        elif REC_ID == 'MRR': retval = MRR(Version, Endian, REC)
        elif REC_ID == 'WCR': retval = WCR(Version, Endian, REC)
        elif REC_ID == 'WIR': retval = WIR(Version, Endian, REC)
        elif REC_ID == 'WRR': retval = WRR(Version, Endian, REC)
        elif REC_ID == 'ADR': retval = ADR(Version, Endian, REC)
        elif REC_ID == 'ASR': retval = ASR(Version, Endian, REC)
        elif REC_ID == 'BPS': retval = BPS(Version, Endian, REC)
        elif REC_ID == 'BRR': retval = BRR(Version, Endian, REC)
        elif REC_ID == 'BSR': retval = BSR(Version, Endian, REC)
        elif REC_ID == 'CNR': retval = CNR(Version, Endian, REC)
        elif REC_ID == 'DTR': retval = DTR(Version, Endian, REC)
        elif REC_ID == 'EPDR': retval = EPDR(Version, Endian, REC)
        elif REC_ID == 'EPS': retval = EPS(Version, Endian, REC)
        elif REC_ID == 'ETSR': retval = ETSR(Version, Endian, REC)
        elif REC_ID == 'FDR': retval = FDR(Version, Endian, REC)
        elif REC_ID == 'FSR': retval = FSR(Version, Endian, REC)
        elif REC_ID == 'GDR': retval = GDR(Version, Endian, REC)
        elif REC_ID == 'GTR': retval = GTR(Version, Endian, REC)
        elif REC_ID == 'HBR': retval = HBR(Version, Endian, REC)
        elif REC_ID == 'IDR': retval = IDR(Version, Endian, REC)
        elif REC_ID == 'MCR': retval = MCR(Version, Endian, REC)
        elif REC_ID == 'MMR': retval = MMR(Version, Endian, REC)
        elif REC_ID == 'MSR': retval = MSR(Version, Endian, REC)
        elif REC_ID == 'NMR': retval = NMR(Version, Endian, REC)
        elif REC_ID == 'PCR': retval = PCR(Version, Endian, REC)
        elif REC_ID == 'PDR': retval = PDR(Version, Endian, REC)
        elif REC_ID == 'PGR': retval = PGR(Version, Endian, REC)
        elif REC_ID == 'PLR': retval = PLR(Version, Endian, REC)
        elif REC_ID == 'PMR': retval = PMR(Version, Endian, REC)
        elif REC_ID == 'PSR': retval = PSR(Version, Endian, REC)
        elif REC_ID == 'RDR': retval = RDR(Version, Endian, REC)
        elif REC_ID == 'SBR': retval = SBR(Version, Endian, REC)
        elif REC_ID == 'SCR': retval = SCR(Version, Endian, REC)
        elif REC_ID == 'SDR': retval = SDR(Version, Endian, REC)
        elif REC_ID == 'SHB': retval = SHB(Version, Endian, REC)
        elif REC_ID == 'SSB': retval = SSB(Version, Endian, REC)
        elif REC_ID == 'SSR': retval = SSR(Version, Endian, REC)
        elif REC_ID == 'STS': retval = STS(Version, Endian, REC)
        elif REC_ID == 'TSR': retval = TSR(Version, Endian, REC)
        elif REC_ID == 'WTR': retval = WTR(Version, Endian, REC)
        elif REC_ID == 'RR1': retval = RR1(Version, Endian, REC) # can not be reached because of -1
        elif REC_ID == 'RR2': retval = RR2(Version, Endian, REC) # can not be reached because of -1
    return retval

def test_main_from_records_py():
    endian = '<'
    version = 'V4'
    rec = b'\x1b\x00\x01P\x00\x00\x08\x00\x01\x02\x03\x04\x05\x06\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    sdr = SDR(version, endian, rec)

    print(len(rec))
    print(sdr)


@pytest.mark.skip
@given(rec=st.binary())
def test_SDR_parse_binary_hypothesis(rec):
    endian = '<'
    version = 'V4'
    sdr = SDR(version, endian, rec)
    print(sdr)


valid_endiannesses = st.one_of(map(st.just, ['<', '>']))
invalid_endiannesses = st.one_of(map(st.just, [None, '', '?']))    # is None valid?
endianesses = valid_endiannesses | invalid_endiannesses

all_records_types = [ATR, BPS, DTR, EPS, FAR, FTR, GDR, HBR, MIR, MPR, MRR,
                     PCR, PGR, PIR, PLR, PMR, PRR, PTR, RDR, SBR, SDR, TSR,
                     WCR, WIR, WRR]


@st.composite
def records(draw):
    record_type = draw(st.one_of(map(st.just, all_records_types)))
    version = 'V4'
    endian = draw(valid_endiannesses)
    return record_type(version, endian)


@pytest.mark.xfail
@given(records())
def test_record_is_printable_hypothesis(record):
    print(record)


@pytest.mark.parametrize("record_type", all_records_types)
def too_verbose_atm_test_record_type_is_constructible_V4(record_type):
    endian = '<'
    version = 'V4'
    record_type(version, endian)


@pytest.mark.parametrize("record_type", all_records_types)
def too_verbose_atm_test_record_is_printable(record_type):
    endian = '<'
    version = 'V4'
    rec = record_type(version, endian)
    print(rec)


@pytest.mark.parametrize("record_type", all_records_types)
def too_verbose_atm_test_record_is_reprable(record_type):
    endian = '<'
    version = 'V4'
    rec = record_type(version, endian)
    rec.__repr__()  # repr checks return type to be string


@pytest.mark.parametrize("record_type,endian",
                         itertools.product(all_records_types, ['<', '>']))
def too_verbose_atm_test_written_bytes_after_read_are_identical(record_type, endian):
    version = 'V4'
    initial_rec = record_type(version, endian)
    initial_rec_bytes = initial_rec.__repr__()
    rec_from_written_bytes = record_type(version, endian, initial_rec_bytes)

    bytes_after_writing_again = rec_from_written_bytes.__repr__()
    assert initial_rec_bytes == bytes_after_writing_again


@pytest.mark.skip
@pytest.mark.parametrize("record_type,endian",
                         itertools.product(all_records_types, ['<', '>']))
def xtest_print_after_write_and_read_is_identical(record_type, endian):
    version = 'V4'
    initial_rec = record_type(version, endian)
    initial_rec_bytes = initial_rec.__repr__()
    rec_from_written_bytes = record_type(version, endian, initial_rec_bytes)

    initial_rec_str = initial_rec.__str__()
    str_after_reading_written_bytes = rec_from_written_bytes.__str__()
    assert initial_rec_str == str_after_reading_written_bytes


def test_PIR_is_printable_with_required_fields():
    endian = '<'
    version = 'V4'
    rec = PIR(version, endian)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    print(rec)


def test_PIR_is_reprable_with_required_fields():
    endian = '<'
    version = 'V4'
    rec = PIR(version, endian)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.__repr__()


def test_PRR_is_printable_with_required_fields():
    endian = '<'
    version = 'V4'
    rec = PRR(version, endian)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.set_value('PART_FLG', ['0', '0', '0', '0', '1', '0', '0', '0'])
    rec.set_value('NUM_TEST', 0)
    rec.set_value('HARD_BIN', 0)
    print(rec)


def test_PRR_is_reprable_with_required_fields():
    endian = '<'
    version = 'V4'
    rec = PRR(version, endian)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.set_value('PART_FLG', ['0', '0', '0', '0', '1', '0', '0', '0'])
    rec.set_value('NUM_TEST', 0)
    rec.set_value('HARD_BIN', 0)
    rec.__repr__()


def test_FAR_set_and_check_all_fields():
    endian = '<'
    version = 'V4'
    rec = FAR(version, endian)
    rec.__repr__()  # important to call to initialize internal stuff! also initialized REC_LEN

    # header
    assert rec.get_value('REC_LEN') == 2
    assert rec.get_value('REC_TYP') == 0
    assert rec.get_value('REC_SUB') == 10

    # initial field values
    assert rec.get_value('CPU_TYPE') == 2  # is this initialized from the current platform?
    assert rec.get_value('STDF_VER') == 4

    # modify CPU_TYPE
    rec.set_value('CPU_TYPE', 128)
    assert rec.get_value('CPU_TYPE') == 128

    # modify STDF_VER
    rec.set_value('STDF_VER', 3)
    assert rec.get_value('STDF_VER') == 3

    # check actually serialized size
    serialized_bytes = rec.__repr__()
    assert len(serialized_bytes) == 4 + 2


def test_MIR_check_default_fields():
    endian = '<'
    version = 'V4'
    rec = MIR(version, endian)

    rec.__repr__()  # important to call to initialize internal stuff!
    #rec = MIR(version, endian, rec.__repr__())

    # header
    assert rec.get_value('REC_LEN') == 15 + 30  # 15 bytes for fixed size fields and 30 variable length strings (1 byte each if empty)
    assert rec.get_value('REC_TYP') == 1
    assert rec.get_value('REC_SUB') == 10

    # initial field values
    assert isinstance(rec.get_value('SETUP_T'), int)  # any unix timestamp, should be now
    #assert rec.get_value('SETUP_T') == 123
    #assert rec.get_value('START_T') == 0  # should be None at this time because no part has been tested yet, but that cannot be stored, so possibly 0 as invalid timestamp?

    # missing invalid data flag is space for the next fields, so this should be the default value?
    assert rec.get_value('MODE_COD') == ' '
    assert rec.get_value('RTST_COD') == ' '
    assert rec.get_value('PROT_COD') == ' '

    assert rec.get_value('BURN_TIM') == 65535

    assert rec.get_value('CMOD_COD') == ' '

    # variable size strings, should be initially empty
    FAR_variable_size_string_field_names = [
        # no explicit missing/invalid flag in spec (initially empty here anyways if not set(?))
        'LOT_ID', 'PART_TYP', 'NODE_NAM', 'TSTR_TYP', 'JOB_NAM',
        # empty explicitly mentioned in spec as missing/invalid
        'JOB_REV', 'SBLOT_ID', 'OPER_NAM', 'EXEC_TYP', 'EXEC_VER', 'TEST_COD',
        'TST_TEMP', 'USER_TXT', 'AUX_FILE', 'PKG_TYP', 'FAMLY_ID', 'DATE_COD',
        'FACIL_ID', 'FLOOR_ID', 'PROC_ID', 'OPER_FRQ', 'SPEC_NAM', 'SPEC_VER',
        'FLOW_ID', 'SETUP_ID', 'DSGN_REV', 'ENG_ID', 'ROM_COD', 'SERL_NUM',
        'SUPR_NAM']
    for field_name in FAR_variable_size_string_field_names:
        assert rec.get_value(field_name) == ''


def test_MIR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = MIR(version, endian)

    rec.set_value('SETUP_T', int(time.time()))
    rec.set_value('START_T', int(time.time()))
    rec.set_value('STAT_NUM', 0)
    rec.set_value('LOT_ID', '123456')
    rec.set_value('PART_TYP', 'MyPart')
    rec.set_value('NODE_NAM', 'MyNode')
    rec.set_value('TSTR_TYP', 'MyTester')
    rec.set_value('JOB_NAM', 'MyJob')

    rec.__repr__()


def test_PIR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = PIR(version, endian)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.__repr__()


def test_PCR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = PCR(version, endian)

    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.set_value('PART_CNT', 10)
    rec.set_value('RTST_CNT', 2)
    rec.set_value('ABRT_CNT', 2)
    rec.set_value('GOOD_CNT', 6)
    rec.set_value('PART_CNT', 10)

    rec.__repr__()


def test_PTR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = PTR(version, endian)

    rec.set_value('TEST_NUM', 123)
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)

    rec.set_value('TEST_FLG', 0b01000000)  # bit 1 === 'RESULT' is valid
    rec.set_value('PARM_FLG', 0)
    rec.set_value('RESULT', 1.5)
    rec.set_value('TEST_TXT', '')
    rec.set_value('ALARM_ID', '')

    # TODO: OPT_FLAG still needs to be initialized, because the missing value (also 255) causes an exception (should be internally stored as list of string...)
    # it is optional according to the spec if it is the last field of the record    
    rec.set_value('OPT_FLAG', 255)  # bit set means ignore some field

    rec.__repr__()


def test_PRR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = PRR(version, endian)

    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)

    rec.set_value('PART_FLG', 0)  # all bits 0 is ok and means part was tested and passed
    rec.set_value('NUM_TEST', 3)
    rec.set_value('HARD_BIN', 0)

    rec.__repr__()


def test_TSR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = TSR(version, endian)
    
    rec.set_value('HEAD_NUM', 1)
    rec.set_value('SITE_NUM', 1)
    rec.set_value('TEST_NUM', 123)

    outbytes = rec.__repr__()


def test_MRR_create_minimal():
    endian = '<'
    version = 'V4'
    rec = MRR(version, endian)

    rec.set_value('FINISH_T', int(time.time()))

    rec.__repr__()


def test_TSR_unpack_truncated():
    endian = '<'
    version = 'V4'
    
    blob_until_optional_fields = b'\x07\x00\x0A\x1e\x01\x01\x20\x7B\x00\x00\x00'
    
    rec = TSR(version, endian, blob_until_optional_fields)
    outputbytes = rec.__repr__()
    
    # TODO: serialization to bytes does not omit optional trailing bytes. this is not a problem but could be optimized
    # assert len(outputbytes) == len(blob_until_optional_fields)
        
    rec2 = TSR(version, endian, outputbytes)
    outputbytes2 = rec.__repr__()
    assert outputbytes == outputbytes2


def test_mir_unpack_truncated():
    endian = '<'
    version = 'V4'
    
    blob_until_optional_fields = b'L\x00\x01\nB\x94K^B\x94K^\x00   \xff\xff \x06123456\x06MyPart\x06MyNode\x08MyTester\x05MyJob'
    
    rec = MIR(version, endian, blob_until_optional_fields)
    outputbytes = rec.__repr__()
    
    # TODO: serialization to bytes does not omit optional trailing bytes. this is not a problem but could be optimized
    # assert len(outputbytes) == len(blob_until_optional_fields)
        
    rec2 = MIR(version, endian, outputbytes)
    outputbytes2 = rec.__repr__()
    assert outputbytes == outputbytes2


def test_create_minimal_stdf():
    endian = '<'
    version = 'V4'
    
    def _create_FAR():
        rec = FAR(version, endian)
        rec.set_value('CPU_TYPE', 2)
        rec.set_value('STDF_VER', 4)
        return rec

    def _create_MIR():
        rec = MIR(version, endian)
        rec.set_value('SETUP_T', int(time.time()))
        rec.set_value('START_T', int(time.time()))
        rec.set_value('STAT_NUM', 0)
        rec.set_value('LOT_ID', '123456')
        rec.set_value('PART_TYP', 'MyPart')
        rec.set_value('NODE_NAM', 'MyNode')
        rec.set_value('TSTR_TYP', 'MyTester')
        rec.set_value('JOB_NAM', 'MyJob')
        return rec

    def _create_PIR():
        rec = PIR(version, endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)
        return rec

    def _create_PTR(test_num: int, result_ispass: bool, result_value: float):
        rec = PTR(version, endian)
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

        return rec

    def _create_PRR(num_tests_executed: int, bin: int):
        rec = PRR(version, endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)

        rec.set_value('PART_FLG', 0)  # all bits 0 is ok and means part was tested and passed
        rec.set_value('NUM_TEST', num_tests_executed)
        rec.set_value('HARD_BIN', bin)

        return rec

    def _create_PCR(num_parts_tested: int):
        rec = PCR(version, endian)
        rec.set_value('HEAD_NUM', 1)
        rec.set_value('SITE_NUM', 1)

        # whats the difference between PART_CNT and FUNC_CNT?
        # is the following always true: RTST_CNT + ABRT_CNT + GOOD_CNT == PART_CNT == FUNC_CNT?
        rec.set_value('PART_CNT', num_parts_tested)
        rec.set_value('RTST_CNT', 0)
        rec.set_value('ABRT_CNT', 0)
        rec.set_value('GOOD_CNT', num_parts_tested)
        rec.set_value('PART_CNT', num_parts_tested)

        return rec

    def _create_MRR():
        rec = MRR(version, endian)
        rec.set_value('FINISH_T', int(time.time()))
        return rec
    
    records = [
        _create_FAR(), _create_MIR(),
        _create_PIR(), _create_PTR(1, True, 1.5), _create_PTR(2, False, 2.5), _create_PRR(2, 1),
        _create_PIR(), _create_PTR(1, True, 1.5), _create_PTR(3, True, 3.5), _create_PRR(2, 2),
        _create_PCR(2), _create_MRR()
    ]

    return records


def test_create_minimal_stdf_bytes():
    records = test_create_minimal_stdf()
    blob = bytes(itertools.chain.from_iterable(rec.__repr__() for rec in records))
    return blob


def test_iterate_minimal_stdf_bytes():
    source_records = test_create_minimal_stdf()
    blob = test_create_minimal_stdf_bytes()
    
    source_record_ids = [rec.id for rec in source_records]
    assert source_record_ids == ['FAR', 'MIR', 'PIR', 'PTR', 'PTR', 'PRR', 'PIR', 'PTR', 'PTR', 'PRR', 'PCR', 'MRR' ]
    
    with io.BytesIO(blob) as stream:
        out_records = [res[3] for res in records_from_file(stream, unpack=True)]
        
    out_record_ids = [rec.id for rec in out_records]
    assert out_record_ids == ['FAR', 'MIR', 'PIR', 'PTR', 'PTR', 'PRR', 'PIR', 'PTR', 'PTR', 'PRR', 'PCR', 'MRR' ]


def print_records_from_file(filename):
    print_ptr_for_next_parts = 10
    endian, version = get_STDF_setup_from_file(filename)
    if endian is not None and version is not None:
        for record in records_from_file(filename, unpack=True):
            REC_LEN, REC_TYP, REC_SUB, REC = record
            if print_ptr_for_next_parts == 0 and REC.id == 'PTR':
                continue
            print(REC.id, ": ", REC.to_dict())
            if REC.id == 'PRR' and print_ptr_for_next_parts > 0:
                print_ptr_for_next_parts -= 1


if __name__ == "__main__":
    #test_written_bytes_after_read_are_identical(MIR, '<')
    #test_PTR_create_minimal()
    print_records_from_file(sys.argv[1])
