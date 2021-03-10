import os
import io
import math
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import FTR

#   Functional Test Record
#   Function:
#   Contains the results of the single execution of a functional test in the
#   test program. Thefirst occurrence of this record also establishes the
#   default values for all semi-staticinformation about the test.
#   The FTR is related to the Test Synopsis Record (TSR) by test number,
#   head number and site number.


def test_FTR():
    ftr("<")
    ftr(">")


def ftr(endian):

    #   ATDF page 51
    expected_atdf = "FTR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 57
    record = FTR(endian=endian)

    test_num = 1
    record.set_value("TEST_NUM", test_num)
    rec_len += 4
    expected_atdf += str(test_num) + "|"

    head_num = 2
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_num = 3
    record.set_value("SITE_NUM", site_num)
    rec_len += 1
    expected_atdf += str(site_num) + "|"

    test_flg = ["1", "0", "1", "1", "1", "1", "0", "1"]
    record.set_value("TEST_FLG", test_flg)
    rec_len += 1
    expected_atdf += "F|"
    expected_atdf += "AUTNX|"

    #    The order of fields is different in STDF and ATDF for FTR record

    #    STDF page 57| ATDF page 51

    #    TEST_NUM    = TEST_NUM
    #    HEAD_NUM    = HEAD_NUM
    #    SITE_NUM    = SITE_NUM
    #    TEST_FLG    -> TEST_FLG bits 6 & 7
    #                -> TEST_FLG bits 0, 2, 3, 4, & 5
    #    OPT_FLAG    -> missing
    #    CYCL_CNT
    #    REL_VADR
    #    REPT_CNT
    #    NUM_FAIL
    #    XFAIL_AD
    #    YFAIL_AD
    #    VECT_OFF
    #    RTN_ICNT    -> missing
    #    PGM_ICNT    -> missing
    #    RTN_INDX
    #    RTN_STAT
    #    PGM_INDX
    #    PGM_STAT
    #    FAIL_PIN
    #    VECT_NAM    = VECT_NAM
    #    TIME_SET    = TIME_SET
    #    OP_CODE
    #    TEST_TXT
    #    ALARM_ID
    #    PROG_TXT
    #    RSLT_TXT
    #    PATG_NUM
    #    SPIN_MAP
    #                = CYCL_CNT
    #                = REL_VADR
    #                = REPT_CNT
    #                = NUM_FAIL
    #                = XFAIL_AD
    #                = YFAIL_AD
    #                = VECT_OFF
    #                = RTN_INDX
    #                = RTN_STAT
    #                = PGM_INDX
    #                = PGM_STAT
    #                = FAIL_PIN
    #                = OP_CODE
    #                = TEST_TXT
    #                = ALARM_ID
    #                = PROG_TXT
    #                = RSLT_TXT
    #                = PATG_NUM
    #                = SPIN_MAP

    opt_flag = ["0", "0", "0", "0", "0", "0", "1", "1"]
    record.set_value("OPT_FLAG", opt_flag)
    rec_len += 1

    cycl_cnt = 4
    record.set_value("CYCL_CNT", cycl_cnt)
    rec_len += 4

    rel_vadr = 5
    record.set_value("REL_VADR", rel_vadr)
    rec_len += 4

    rept_cnt = 6
    record.set_value("REPT_CNT", rept_cnt)
    rec_len += 4

    num_fail = 7
    record.set_value("NUM_FAIL", num_fail)
    rec_len += 4

    xfail_ad = 8
    record.set_value("XFAIL_AD", xfail_ad)
    rec_len += 4

    yfail_ad = 9
    record.set_value("YFAIL_AD", yfail_ad)
    rec_len += 4

    vect_off = 10
    record.set_value("VECT_OFF", vect_off)
    rec_len += 2

    rtn_icnt = 11
    record.set_value("RTN_ICNT", rtn_icnt)
    rec_len += 2

    pgm_icnt = 12
    record.set_value("PGM_ICNT", pgm_icnt)
    rec_len += 2

    rtn_indx = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    record.set_value("RTN_INDX", rtn_indx)
    rec_len += len(rtn_indx) * 2

    rtn_stat = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    record.set_value("RTN_STAT", rtn_stat)
    rec_len += math.ceil(len(rtn_stat) / 2)

    pgm_indx = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    record.set_value("PGM_INDX", pgm_indx)
    rec_len += len(pgm_indx) * 2

    pgm_stat = [0, 1, 0, 1, 2, 3, 2, 3, 4, 5, 6, 7]
    record.set_value("PGM_STAT", pgm_stat)
    rec_len += math.ceil(len(pgm_stat) / 2)

    fail_pin = ["1", "0", "1", "1", "1", "1", "1", "1", "0", "1", "1", "1"]
    record.set_value("FAIL_PIN", fail_pin)
    rec_len += math.ceil(len(fail_pin) / 8) + 2

    vect_nam = "ATPG_FULL_SCAN.stil"
    record.set_value("VECT_NAM", vect_nam)
    rec_len += len(vect_nam) + 1
    expected_atdf += str(vect_nam) + "|"

    time_set = "FAST"
    record.set_value("TIME_SET", time_set)
    rec_len += len(time_set) + 1
    expected_atdf += str(time_set) + "|"

    expected_atdf += str(cycl_cnt) + "|"
    expected_atdf += str(rel_vadr) + "|"
    expected_atdf += str(rept_cnt) + "|"
    expected_atdf += str(num_fail) + "|"
    expected_atdf += str(xfail_ad) + "|"
    expected_atdf += str(yfail_ad) + "|"
    expected_atdf += str(vect_off) + "|"
    #   RTN_INDX
    expected_atdf += "1,2,3,4,5,6,7,8,9,10,11|"
    #   RTN_STAT
    expected_atdf += "1,2,3,4,5,6,7,8,9,10,11|"
    #   PGM_INDX
    expected_atdf += "1,2,3,4,5,6,7,8,9,10,11,12|"
    #   PGM_STAT
    expected_atdf += "0,1,0,1,2,3,2,3,4,5,6,7|"
    #   FAIL_PIN
    expected_atdf += "1,0,1,1,1,1,1,1,0,1,1,1|"

    op_code = "NONE"
    record.set_value("OP_CODE", op_code)
    rec_len += len(op_code) + 1
    expected_atdf += str(op_code) + "|"

    test_txt = "SCAN"
    record.set_value("TEST_TXT", test_txt)
    rec_len += len(test_txt) + 1
    expected_atdf += str(test_txt) + "|"

    alarm_id = "OVP"
    record.set_value("ALARM_ID", alarm_id)
    rec_len += len(alarm_id) + 1
    expected_atdf += str(alarm_id) + "|"

    prog_txt = "NONE"
    record.set_value("PROG_TXT", prog_txt)
    rec_len += len(prog_txt) + 1
    expected_atdf += str(prog_txt) + "|"

    rslt_txt = "NONE"
    record.set_value("RSLT_TXT", rslt_txt)
    rec_len += len(rslt_txt) + 1
    expected_atdf += str(rslt_txt) + "|"

    patg_num = 0
    record.set_value("PATG_NUM", patg_num)
    rec_len += 1
    expected_atdf += str(patg_num) + "|"

    spin_map = [
        "1",
        "1",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "1",
        "1",
        "0",
        "0",
        "1",
        "1",
        "0",
        "0",
    ]
    record.set_value("SPIN_MAP", spin_map)
    rec_len += math.ceil(len(spin_map) / 8) + 2
    expected_atdf += "1,1,0,0,0,0,0,0,1,1,0,0,1,1,0,0"

    #    Test serialization
    #    1. Save MPR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 15, 20)
    #   Test TEST_NUM, expected value test_num
    stdfRecTest.assert_int(4, test_num)
    #   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
    #   Test TEST_FLAG, expected value test_flg
    stdfRecTest.assert_bits(test_flg)
    #   Test OPT_FLAG, expected value opt_flg
    stdfRecTest.assert_bits(opt_flag)
    #   Test CYCL_CNT, expected value cycl_cnt
    stdfRecTest.assert_int(4, cycl_cnt)
    #   Test REL_VADR, expected value rel_vadr
    stdfRecTest.assert_int(4, rel_vadr)
    #   Test REPT_CNT, expected value rept_cnt
    stdfRecTest.assert_int(4, rept_cnt)
    #   Test NUM_FAIL, expected value num_fail
    stdfRecTest.assert_int(4, num_fail)
    #   Test XFAIL_AD, expected value xfail_ad
    stdfRecTest.assert_int(4, xfail_ad)
    #   Test YFAIL_AD, expected value yfail_ad
    stdfRecTest.assert_int(4, yfail_ad)
    #   Test VECT_OFF, expected value vect_off
    stdfRecTest.assert_int(2, vect_off)
    #   Test RTN_ICNT, expected value rtn_icnt
    stdfRecTest.assert_int(2, rtn_icnt)
    #   Test PGM_ICNT, expected value pgm_icnt
    stdfRecTest.assert_int(2, pgm_icnt)
    #   Test RTN_INDX, expected value rtn_indx
    stdfRecTest.assert_int_array(2, rtn_indx)
    #   Test RTN_STAT, expected value rtn_stat
    stdfRecTest.assert_nibble_array(rtn_icnt, rtn_stat)
    #   Test PGM_INDX, expected value pgm_indx
    stdfRecTest.assert_int_array(2, pgm_indx)
    #   Test PGM_STAT, expected value pgm_stat
    stdfRecTest.assert_nibble_array(pgm_icnt, pgm_stat)
    #   Test FAIL_PIN, expected value fail_pin
    #    stdfRecTest.assert_var_bits(fail_pin_len, fail_pin)
    stdfRecTest.assert_var_bits(fail_pin)
    #   Test VECT_NAM, expected length of the string and value of the vect_nam
    stdfRecTest.assert_ubyte(len(vect_nam))
    stdfRecTest.assert_char_array(len(vect_nam), vect_nam)
    #   Test TIME_SET, expected length of the string and value of the time_set
    stdfRecTest.assert_ubyte(len(time_set))
    stdfRecTest.assert_char_array(len(time_set), time_set)
    #   Test OP_CODE, expected length of the string and value of the op_code
    stdfRecTest.assert_ubyte(len(op_code))
    stdfRecTest.assert_char_array(len(op_code), op_code)
    #   Test TEST_TXT, expected length of the string and value of the test_txt
    stdfRecTest.assert_ubyte(len(test_txt))
    stdfRecTest.assert_char_array(len(test_txt), test_txt)
    #   Test ALARM_ID, expected length of the string and value of the alarm_id
    stdfRecTest.assert_ubyte(len(alarm_id))
    stdfRecTest.assert_char_array(len(alarm_id), alarm_id)
    #   Test PROG_TXT, expected length of the string and value of the prog_txt
    stdfRecTest.assert_ubyte(len(prog_txt))
    stdfRecTest.assert_char_array(len(prog_txt), prog_txt)
    #   Test RSLT_TXT, expected length of the string and value of the rslt_txt
    stdfRecTest.assert_ubyte(len(rslt_txt))
    stdfRecTest.assert_char_array(len(rslt_txt), rslt_txt)
    #   Test PATG_NUM, expected value patg_num
    stdfRecTest.assert_int(1, patg_num)
    #   Test SPIN_MAP, expected value spin_map
    #    stdfRecTest.assert_var_bits(spin_map_len, spin_map)
    stdfRecTest.assert_var_bits(spin_map)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = FTR("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 15, 20)
    #   Test TEST_NUM, position 3, value of test_num variable
    stdfRecTest.assert_instance_field(inst, 3, test_num)
    #   Test HEAD_NUM, position 4, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 4, head_num)
    #   Test SITE_NUM, position 5, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 5, site_num)
    #   Test TEST_FLG, position 6, value of test_flg variable
    stdfRecTest.assert_instance_field(inst, 6, test_flg)
    #   Test OPT_FLAG, position 7, value of opt_flag variable
    stdfRecTest.assert_instance_field(inst, 7, opt_flag)
    #   Test CYCL_CNT, position 8, value of cycl_cnt variable
    stdfRecTest.assert_instance_field(inst, 8, cycl_cnt)
    #   Test REL_VADR, position 9, value of rel_vadr variable
    stdfRecTest.assert_instance_field(inst, 9, rel_vadr)
    #   Test REPT_CNT, position 10, value of rept_cnt variable
    stdfRecTest.assert_instance_field(inst, 10, rept_cnt)
    #   Test NUM_FAIL, position 11, value of num_fail variable
    stdfRecTest.assert_instance_field(inst, 11, num_fail)
    #   Test XFAIL_AD, position 12, value of xfail_ad variable
    stdfRecTest.assert_instance_field(inst, 12, xfail_ad)
    #   Test YFAIL_AD, position 13, value of yfail_ad variable
    stdfRecTest.assert_instance_field(inst, 13, yfail_ad)
    #   Test VECT_OFF, position 14, value of vect_off variable
    stdfRecTest.assert_instance_field(inst, 14, vect_off)
    #   Test RTN_ICNT, position 15, value of rtn_icnt variable
    stdfRecTest.assert_instance_field(inst, 15, rtn_icnt)
    #   Test PGM_ICNT, position 16, value of pgm_icnt variable
    stdfRecTest.assert_instance_field(inst, 16, pgm_icnt)
    #   Test RTN_INDX, position 17, value of rtn_indx variable
    stdfRecTest.assert_instance_field(inst, 17, rtn_indx)
    #   Test RTN_STAT, position 18, value of rtn_stat variable
    stdfRecTest.assert_instance_field(inst, 18, rtn_stat)
    #   Test PGM_INDX, position 19, value of pgm_indx variable
    stdfRecTest.assert_instance_field(inst, 19, pgm_indx)
    #   Test PGM_STAT, position 20, value of pgm_stat variable
    stdfRecTest.assert_instance_field(inst, 20, pgm_stat)
    #   Test FAIL_PIN, position 21, value of fail_pin variable
    stdfRecTest.assert_instance_field(inst, 21, fail_pin)
    #   Test VECT_NAM, position 22, value of vect_nam variable
    stdfRecTest.assert_instance_field(inst, 22, vect_nam)
    #   Test TIME_SET, position 23, value of time_set variable
    stdfRecTest.assert_instance_field(inst, 23, time_set)
    #   Test OP_CODE, position 24, value of op_code variable
    stdfRecTest.assert_instance_field(inst, 24, op_code)
    #   Test TEST_TXT, position 25, value of test_txt variable
    stdfRecTest.assert_instance_field(inst, 25, test_txt)
    #   Test ALARM_ID, position 26, value of alarm_id variable
    stdfRecTest.assert_instance_field(inst, 26, alarm_id)
    #   Test PROG_TXT, position 27, value of prog_txt variable
    stdfRecTest.assert_instance_field(inst, 27, prog_txt)
    #   Test RSLT_TXT, position 28, value of rslt_txt variable
    stdfRecTest.assert_instance_field(inst, 28, rslt_txt)
    #   Test PATG_NUM, position 29, value of patg_num variable
    stdfRecTest.assert_instance_field(inst, 29, patg_num)
    #   Test SPIN_MAP, position 30, value of spin_map variable
    stdfRecTest.assert_instance_field(inst, 30, spin_map)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf


#   ToDo: Test reset method and OPT_FLAG

#   ToDo: Test JSON output
