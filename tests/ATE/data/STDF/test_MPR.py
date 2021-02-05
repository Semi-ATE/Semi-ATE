import os
import math
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import MPR


#   Multiple-Result Parametric Record
#   Function:
#   Contains the results of a single execution of a parametric test in the test 
#   programwhere that test returns multiple values. The first occurrence of 
#   this record alsoestablishes the default values for all semi-static 
#   information about the test, such aslimits, units, and scaling. TheMPRis 
#   related to the Test Synopsis Record (TSR)bytestnumber, head number, and 
#   site number.
    
def test_MPR():
    
#   ATDF page 47
    expected_atdf = "MPR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 53
    record = MPR()
    
    test_num = 1
    record.set_value('TEST_NUM', test_num)
    rec_len += 4;
    expected_atdf += str(test_num) +"|"

    head_num = 2
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) +"|"

    site_num = 3
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"

#    The order of fields is different in STDF and ATDF for FTR record
    
#    STDF page 53| ATDF page 47
    
#    TEST_NUM    = TEST_NUM   
#    HEAD_NUM    = HEAD_NUM    
#    SITE_NUM    = SITE_NUM  
#    TEST_FLG    
#    PARM_FLG            
#    RTN_ICNT    -> missing

#    RSLT_CNT    -> missing    
#    RTN_STAT    = RTN_STAT  
#    RTN_RSLT    = RTN_RSLT
#                -> TEST_FLG bits 6 & 7 PARM_FLG bit 5
#                -> TEST_FLG bits 0, 2, 3, 4 & 5 PARM_FLG bits 0, 1, 2, 3 & 4
#    TEST_TXT    = TEST_TXT 
#    ALARM_ID    = ALARM_ID 
#                -> PARM_FLG bits 6 & 7 
#    OPT_FLAG 
#    RES_SCAL
#    LLM_SCAL
#    HLM_SCAL
#    LO_LIMIT
#    HI_LIMIT
#    START_IN
#    INCR_IN
#    RTN_INDX
#    UNITS       = UNITS 
#    UNITS_IN
#    C_RESFMT
#    C_LLMFMT
#    C_HLMFMT
#    LO_SPEC
#    HI_SPEC
#                = LO_LIMIT
#                = HI_LIMIT
#                = START_IN
#                = INCR_IN
#                = UNITS_IN
#                = RTN_INDX
#                = C_RESFMT
#                = C_LLMFMT
#                = C_HLMFMT
#                = LO_SPEC
#                = HI_SPEC
#                = RES_SCAL
#                = LLM_SCAL
#                = HLM_SCAL

    test_flg = ['1', '0', '1', '1', '1', '1', '0', '1']
    record.set_value('TEST_FLG', test_flg)
    rec_len += 1;

    parm_flg = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('PARM_FLG', parm_flg)
    rec_len += 1;
    
    rtn_icnt = 11
    record.set_value('RTN_ICNT', rtn_icnt)
    rec_len += 2;

    rslt_cnt = 12
    record.set_value('RSLT_CNT', rslt_cnt)
    rec_len += 2;

    rtn_stat = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    record.set_value('RTN_STAT', rtn_stat)
    rec_len += math.ceil(len(rtn_stat)/2)
    expected_atdf += "1,2,3,4,5,6,7,8,9,10,11|"

    rtn_rslt = [ 0.123, 1.321, 0.4567, 1.22453, 2.32115, 3.87643, 2.214253, 3.24212, 4.13411, 5.1, 6.1, 7.1]
    record.set_value('RTN_RSLT', rtn_rslt)
    rec_len += len(rtn_rslt)*4
    expected_atdf += "0.123,1.321,0.4567,1.22453,2.32115,3.87643,2.214253,3.24212,4.13411,5.1,6.1,7.1|"

#   TEST_FLG bits 6&7 and PARM_FLG bit 5
    expected_atdf += "FA|"
#   TEST_FLG bits 0,2,3,4 & 5 and PARM_FLG bits 0, 1, 2, 3 & 4
    expected_atdf += "AUTNXSDOHL|"

    test_txt = 'SCAN'
    record.set_value('TEST_TXT', test_txt)
    rec_len += len(test_txt) + 1;
    expected_atdf += str(test_txt) + "|"

    alarm_id = 'OVP'
    record.set_value('ALARM_ID', alarm_id)
    rec_len += len(alarm_id) + 1;
    expected_atdf += str(alarm_id) + "|"

#   PARM_FLG bits 6 & 7
    expected_atdf += "LH|"
    
    opt_flag = ['0', '0', '0', '0', '0', '0', '1', '1']
    record.set_value('OPT_FLAG', opt_flag)
    rec_len += 1;

    res_scal = 10
    record.set_value('RES_SCAL', res_scal)
    rec_len += 1;

    llm_scal = 10
    record.set_value('LLM_SCAL', llm_scal)
    rec_len += 1;

    hlm_scal = 10
    record.set_value('HLM_SCAL', hlm_scal)
    rec_len += 1;

    lo_limit = 1.001
    record.set_value('LO_LIMIT', lo_limit)
    rec_len += 4;
    
    hi_limit = 1.999
    record.set_value('HI_LIMIT', hi_limit)
    rec_len += 4;

    start_in = 2.5
    record.set_value('START_IN', start_in)
    rec_len += 4;

    incr_in = 1.125
    record.set_value('INCR_IN', incr_in)
    rec_len += 4;
    
    rtn_indx = [ 1, 2, 3, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000]
    record.set_value('RTN_INDX', rtn_indx)
    rec_len += len(rtn_indx)*2;

    units = 'V'
    record.set_value('UNITS', units)
    rec_len += len(units) + 1;
    expected_atdf += str(units) + "|"

    units_in = 'mV'
    record.set_value('UNITS_IN', units_in)
    rec_len += len(units_in) + 1;

    c_resfmt = '%3.3f'
    record.set_value('C_RESFMT', c_resfmt)
    rec_len += len(c_resfmt) + 1;

    c_llmfmt = '%3.6f'
    record.set_value('C_LLMFMT', c_llmfmt)
    rec_len += len(c_llmfmt) + 1;

    c_hlmfmt = '%3.6f'
    record.set_value('C_HLMFMT', c_hlmfmt)
    rec_len += len(c_hlmfmt) + 1;

    lo_spec = 1.001
    record.set_value('LO_SPEC', lo_spec)
    rec_len += 4;
    
    hi_spec = 1.999
    record.set_value('HI_SPEC', hi_spec)
    rec_len += 4;

#   LO_LIMIT
    expected_atdf += str(lo_limit) + "|"
#   HI_LIMIT
    expected_atdf += str(hi_limit) + "|"
#   START_IN
    expected_atdf += str(start_in) + "|"
#   INCR_IN
    expected_atdf += str(incr_in) + "|"
#   UNITS_IN
    expected_atdf += str(units_in) + "|"
#   RTN_INDX
    expected_atdf += "1,2,3,4000,5000,6000,7000,8000,9000,10000,11000|"
#   C_RESFMT
    expected_atdf += str(c_resfmt) + "|"
#   C_LLMFMT
    expected_atdf += str(c_llmfmt) + "|"
#   C_HLMFMT
    expected_atdf += str(c_hlmfmt) + "|"
#   LO_SPEC
    expected_atdf += str(lo_spec) + "|"
#   HI_SPEC
    expected_atdf += str(hi_spec) + "|"
#   RES_SCAL
    expected_atdf += str(res_scal) + "|"
#   LLM_SCAL
    expected_atdf += str(llm_scal) + "|"
#   HLM_SCAL
    expected_atdf += str(hlm_scal) + "|"
    

#    Test serialization
#    1. Save MPR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  

    f = open(tf.name, "wb")
    
    w_data = record.__repr__()
    f.write(w_data)
    f.close
    
    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 15, 15)
#   Test TEST_NUM, expected value test_num
    stdfRecTest.assert_int(4, test_num)
#   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
#   Test TEST_FLG, expected value test_flg
    stdfRecTest.assert_bits(test_flg)
#   Test PARM_FLG, expected value parm_flg
    stdfRecTest.assert_bits(parm_flg)
#   Test RTN_ICNT, expected value rtn_icnt
    stdfRecTest.assert_int(2, rtn_icnt)
#   Test RSLT_CNT, expected value rslt_cnt
    stdfRecTest.assert_int(2, rslt_cnt)
#   Test RTN_STAT, expected value rtn_stat
    stdfRecTest.assert_nibble_array(rtn_icnt, rtn_stat)
#   Test RTN_RSLT, expected value rtn_rslt
    stdfRecTest.assert_float_array(rtn_rslt)
#   Test TEST_TXT, expected length of the string and value of the test_txt
    stdfRecTest.assert_ubyte(len(test_txt))
    stdfRecTest.assert_char_array(len(test_txt), test_txt);
#   Test ALARM_ID, expected length of the string and value of the alarm_id
    stdfRecTest.assert_ubyte(len(alarm_id))
    stdfRecTest.assert_char_array(len(alarm_id), alarm_id);
#   Test OPT_FLAG, expected value opt_flg
    stdfRecTest.assert_bits(opt_flag)
#   Test RES_SCAL, expected value res_scal
    stdfRecTest.assert_int(1, res_scal)
#   Test LLM_SCAL, expected value llm_scal
    stdfRecTest.assert_int(1, llm_scal)
#   Test HLM_SCAL, expected value hlm_scal
    stdfRecTest.assert_int(1, hlm_scal)
#   Test LO_LIMIT, expected value lo_limit
    stdfRecTest.assert_float(lo_limit)
#   Test HI_LIMIT, expected value hi_limit
    stdfRecTest.assert_float(hi_limit)
#   Test START_IN, expected value start_in
    stdfRecTest.assert_float(start_in)
#   Test INCR_IN, expected value incr_in
    stdfRecTest.assert_float(incr_in)
#   Test RTN_INDX, expected value rtn_indx
    stdfRecTest.assert_int_array(2, rtn_indx)
#   Test UNITS, expected value units
    stdfRecTest.assert_ubyte(len(units))
    stdfRecTest.assert_char_array(len(units), units)
#   Test UNITS_IN, expected value units_in
    stdfRecTest.assert_ubyte(len(units_in))
    stdfRecTest.assert_char_array(len(units_in), units_in)
#   Test C_RESFMT, expected value c_resfmt
    stdfRecTest.assert_ubyte(len(c_resfmt))
    stdfRecTest.assert_char_array(len(c_resfmt), c_resfmt)
#   Test C_LLMFMT, expected value c_llmfmt
    stdfRecTest.assert_ubyte(len(c_llmfmt))
    stdfRecTest.assert_char_array(len(c_llmfmt), c_llmfmt)
#   Test C_HLMFMT, expected value c_hlmfmt
    stdfRecTest.assert_ubyte(len(c_hlmfmt))
    stdfRecTest.assert_char_array(len(c_hlmfmt), c_hlmfmt)
#   Test LO_SPEC, expected value lo_spec
    stdfRecTest.assert_float(lo_spec)
#   Test HI_SPEC, expected value hi_spec
    stdfRecTest.assert_float(hi_spec)

    
    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = MPR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 15, 15)
#   Test TEST_NUM, position 3, value of test_num variable
    stdfRecTest.assert_instance_field(inst, 3, test_num);
#   Test HEAD_NUM, position 4, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 4, head_num);
#   Test SITE_NUM, position 5, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 5, site_num);
#   Test TEST_FLG, position 6, value of test_flg variable
    stdfRecTest.assert_instance_field(inst, 6, test_flg);
#   Test PARM_FLG, position 7, value of parm_flg variable
    stdfRecTest.assert_instance_field(inst, 7, parm_flg);
#   Test RTN_ICNT, position 8, value of rtn_icnt variable
    stdfRecTest.assert_instance_field(inst, 8, rtn_icnt);
#   Test RSLT_CNT, position 9, value of rslt_cnt variable
    stdfRecTest.assert_instance_field(inst, 9, rslt_cnt);
#   Test RTN_STAT, position 10, value of rtn_stat variable
    stdfRecTest.assert_instance_field(inst, 10, rtn_stat);
#   Test RTN_RSLT, position 11, value of rtn_rslt variable
    stdfRecTest.assert_instance_field(inst, 11, rtn_rslt);
#   Test TEST_TXT, position 12, value of test_txt variable
    stdfRecTest.assert_instance_field(inst, 12, test_txt);
#   Test ALARM_ID, position 13, value of alarm_id variable
    stdfRecTest.assert_instance_field(inst, 13, alarm_id);
#   Test OPT_FLAG, position 14, value of opt_flag variable
    stdfRecTest.assert_instance_field(inst, 14, opt_flag);
#   Test RES_SCAL, position 15, value of res_scal variable
    stdfRecTest.assert_instance_field(inst, 15, res_scal);
#   Test LLM_SCAL, position 16, value of llm_scal variable
    stdfRecTest.assert_instance_field(inst, 16, llm_scal);
#   Test HLM_SCAL, position 17, value of hlm_scal variable
    stdfRecTest.assert_instance_field(inst, 17, hlm_scal);
#   Test LO_LIMIT, position 18, value of lo_limit variable
    stdfRecTest.assert_instance_field(inst, 18, lo_limit);
#   Test HI_LIMIT, position 19, value of hi_limit variable
    stdfRecTest.assert_instance_field(inst, 19, hi_limit);
#   Test START_IN, position 20, value of start_in variable
    stdfRecTest.assert_instance_field(inst, 20, start_in);
#   Test INCR_IN, position 21, value of incr_in variable
    stdfRecTest.assert_instance_field(inst, 21, incr_in);
#   Test RTN_INDX, position 22, value of rtn_indx variable
    stdfRecTest.assert_instance_field(inst, 22, rtn_indx);
#   Test UNITS, position 23, value of units variable
    stdfRecTest.assert_instance_field(inst, 23, units);
#   Test UNITS_IN, position 21, value of units_in variable
    stdfRecTest.assert_instance_field(inst, 24, units_in);
#   Test C_RESFMT, position 25, value of c_resfmt variable
    stdfRecTest.assert_instance_field(inst, 25, c_resfmt);
#   Test C_LLMFMT, position 26, value of c_llmfmt variable
    stdfRecTest.assert_instance_field(inst, 26, c_llmfmt);
#   Test C_HLMFMT, position 27, value of c_hlmfmt variable
    stdfRecTest.assert_instance_field(inst, 27, c_hlmfmt);
#   Test LO_SPEC, position 28, value of lo_spec variable
    stdfRecTest.assert_instance_field(inst, 28, lo_spec);
#   Test HI_SPEC, position 29, value of hi_spec variable
    stdfRecTest.assert_instance_field(inst, 29, hi_spec);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf
 
    os.remove(tf.name)

#   Test reset method and OPT_FLAG
    rec_len = 0;
    record.reset()

    test_num = 11
    record.set_value('TEST_NUM', test_num)
    rec_len += 4;
    expected_atdf += str(test_num) +"|"

    head_num = 22
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) +"|"

    site_num = 33
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"

    test_flg = ['0', '0', '0', '0', '0', '0', '0', '0']
    record.set_value('TEST_FLG', test_flg)
    rec_len += 1;

    parm_flg = ['0', '0', '0', '0', '0', '0', '0', '0']
    record.set_value('PARM_FLG', parm_flg)
    rec_len += 1;
    
    rtn_icnt = 12
    record.set_value('RTN_ICNT', rtn_icnt)
    rec_len += 2;

    rslt_cnt = 13
    record.set_value('RSLT_CNT', rslt_cnt)
    rec_len += 2;

    rtn_stat = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    record.set_value('RTN_STAT', rtn_stat)
    rec_len += math.ceil(len(rtn_stat)/2)
    expected_atdf += "1,2,3,4,5,6,7,8,9,10,11,12|"

    rtn_rslt = [ 0.123, 1.321, 0.4567, 1.22453, 2.32115, 3.87643, 2.214253, 3.24212, 4.13411, 5.1, 6.1, 7.1, 9.9999]
    record.set_value('RTN_RSLT', rtn_rslt)
    rec_len += len(rtn_rslt)*4
    expected_atdf += "0.123,1.321,0.4567,1.22453,2.32115,3.87643,2.214253,3.24212,4.13411,5.1,6.1,7.1,9.9999|"

#   TEST_FLG bits 6&7 and PARM_FLG bit 5
    expected_atdf += "|"
#   TEST_FLG bits 0,2,3,4 & 5 and PARM_FLG bits 0, 1, 2, 3 & 4
    expected_atdf += "|"

    test_txt = 'SCAN_IDDQ'
    record.set_value('TEST_TXT', test_txt)
    rec_len += len(test_txt) + 1;
    expected_atdf += str(test_txt) + "|"

    alarm_id = 'OVP_SMU'
    record.set_value('ALARM_ID', alarm_id)
    rec_len += len(alarm_id) + 1;
    expected_atdf += str(alarm_id) + "|"

#   PARM_FLG bits 6 & 7
    expected_atdf += "|"
    
    opt_flag = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('OPT_FLAG', opt_flag)
    rec_len += 1;

    f = open(tf.name, "wb")
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")

    inst = MPR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 15, 15)

#   ToDo: Test JSON output
