import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import TSR

#   Test Synopsis Record
#   Function:
#   Contains the test execution and failure counts for one parametric or
#   functional test inthe test program. Also contains static information,
#   such as test name. TheTSRisrelated to the Functional Test Record (FTR),
#   the Parametric Test Record (PTR), and theMultiple Parametric Test Record
#   (MPR) by test number, head number, and sitenumber.


def test_TSR():
    tsr("<")
    tsr(">")


def tsr(end):

    #   ATDF page 41
    expected_atdf = "TSR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 45
    record = TSR(endian=end)

    head_num = 1
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_num = 1
    record.set_value("SITE_NUM", site_num)
    rec_len += 1
    expected_atdf += str(site_num) + "|"

    #    The order of fields is different in STDF and ATDF for TSR record
    #
    #    STDF page 45| ATDF page 41
    #
    #    HEAD_NUM    = HEAD_NUM
    #    STEP_NUM    = STEP_NUM
    #    TEST_TYP
    #    TEST_NUM    = TEST_NUM
    #    EXEC_CNT
    #    FAIL_CNT
    #    ALRM_CNT
    #    TEST_NAM    = TEST_NAM
    #                  TEST_TYP
    #                  EXEC_CNT
    #                  FAIL_CNT
    #                  ALRM_CNT
    #    SEQ_NAME    = SEQ_NAME
    #    TEST_LBL    = TEST_LBL
    #    OPT_FLAG    > missing
    #    TEST_TIM    = TEST_TIM
    #    TEST_MIN    = TEST_MIN
    #    TEST_MAX    = TEST_MAX
    #    TST_SUMS    = TST_SUMS
    #    TST_SQRS    = TST_SQRS

    test_typ = "P"
    record.set_value("TEST_TYP", test_typ)
    rec_len += 1

    test_num = 123
    record.set_value("TEST_NUM", test_num)
    rec_len += 4
    expected_atdf += str(test_num) + "|"

    exec_cnt = 123
    record.set_value("EXEC_CNT", exec_cnt)
    rec_len += 4

    fail_cnt = 2
    record.set_value("FAIL_CNT", fail_cnt)
    rec_len += 4

    alrm_cnt = 0
    record.set_value("ALRM_CNT", alrm_cnt)
    rec_len += 4

    test_nam = "IDDQ"
    record.set_value("TEST_NAM", test_nam)
    rec_len += len(test_nam) + 1
    expected_atdf += test_nam + "|"

    expected_atdf += test_typ + "|"

    expected_atdf += str(exec_cnt) + "|"
    expected_atdf += str(fail_cnt) + "|"
    expected_atdf += str(alrm_cnt) + "|"

    seq_name = "STD FLOW"
    record.set_value("SEQ_NAME", seq_name)
    rec_len += len(seq_name) + 1
    expected_atdf += seq_name + "|"

    test_lbl = "label"
    record.set_value("TEST_LBL", test_lbl)
    rec_len += len(test_lbl) + 1
    expected_atdf += test_lbl + "|"

    opt_flag = ["1", "1", "0", "0", "1", "0", "0", "0"]
    record.set_value("OPT_FLAG", opt_flag)
    rec_len += 1
    expected_atdf += ""

    test_tim = 2.345
    record.set_value("TEST_TIM", test_tim)
    rec_len += 4
    expected_atdf += str(test_tim) + "|"

    test_min = 1.234
    record.set_value("TEST_MIN", test_min)
    rec_len += 4
    expected_atdf += str(test_min) + "|"

    test_max = 1.321
    record.set_value("TEST_MAX", test_max)
    rec_len += 4
    expected_atdf += str(test_max) + "|"

    tst_sums = 1213.321
    record.set_value("TST_SUMS", tst_sums)
    rec_len += 4
    expected_atdf += str(tst_sums) + "|"

    tst_sqrs = 34.83420
    record.set_value("TST_SQRS", tst_sqrs)
    rec_len += 4
    expected_atdf += str(tst_sqrs)

    #    Test serialization
    #    1. Save TSR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 10, 30)
    #   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
    #   Test TEST_TYP, expected value test_type
    stdfRecTest.assert_char(test_typ)
    #   Test TEST_NUM, expected value test_num
    stdfRecTest.assert_int(4, test_num)
    #   Test EXEC_CNT, expected value exec_cnt
    stdfRecTest.assert_int(4, exec_cnt)
    #   Test FAIL_CNT, expected value fail_cnt
    stdfRecTest.assert_int(4, fail_cnt)
    #   Test ALRM_CNT, expected value alrm_cnt
    stdfRecTest.assert_int(4, alrm_cnt)
    #   Test TEST_NAM, expected value test_nam
    stdfRecTest.assert_ubyte(len(test_nam))
    stdfRecTest.assert_char_array(len(test_nam), test_nam)
    #   Test SEQ_NAME, expected value seq_name
    stdfRecTest.assert_ubyte(len(seq_name))
    stdfRecTest.assert_char_array(len(seq_name), seq_name)
    #   Test TEST_LBL, expected value test_lbl
    stdfRecTest.assert_ubyte(len(test_lbl))
    stdfRecTest.assert_char_array(len(test_lbl), test_lbl)
    #   Test OPT_FLAG, expected value opt_flag
    stdfRecTest.assert_bits(opt_flag)
    #   Test TEST_TIM, expected value test_tim
    stdfRecTest.assert_float(test_tim)
    #   Test TEST_MIN, expected value test_min
    stdfRecTest.assert_float(test_min)
    #   Test TEST_MAX, expected value test_max
    stdfRecTest.assert_float(test_max)
    #   Test TST_SUMS, expected value tst_sums
    stdfRecTest.assert_float(tst_sums)
    #   Test TST_SQRS, expected value tst_sqrs
    stdfRecTest.assert_float(tst_sqrs)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = TSR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 10, 30)
    #   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num)
    #   Test SITE_NUM, position 4, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 4, site_num)
    #   Test TEST_TYP, position 5, value of test_typ variable
    stdfRecTest.assert_instance_field(inst, 5, test_typ)
    #   Test TEST_NUM, position 6, value of test_num variable
    stdfRecTest.assert_instance_field(inst, 6, test_num)
    #   Test EXEC_CNT, position 7, value of exec_cnt variable
    stdfRecTest.assert_instance_field(inst, 7, exec_cnt)
    #   Test FAIL_CNT, position 8, value of fail_cnt variable
    stdfRecTest.assert_instance_field(inst, 8, fail_cnt)
    #   Test ALRM_CNT, position 9, value of alrm_cnt variable
    stdfRecTest.assert_instance_field(inst, 9, alrm_cnt)
    #   Test TEST_NAM, position 10, value of test_nam variable
    stdfRecTest.assert_instance_field(inst, 10, test_nam)
    #   Test SEQ_NAME, position 11, value of seq_name variable
    stdfRecTest.assert_instance_field(inst, 11, seq_name)
    #   Test TEST_LBL, position 12, value of test_lbl variable
    stdfRecTest.assert_instance_field(inst, 12, test_lbl)
    #   Test OPT_FLAG, position 13, value of opt_flag variable
    stdfRecTest.assert_instance_field(inst, 13, opt_flag)
    #   Test TEST_TIM, position 14, value of test_tim variable
    stdfRecTest.assert_instance_field(inst, 14, test_tim)
    #   Test TEST_MIN, position 15, value of test_min variable
    stdfRecTest.assert_instance_field(inst, 15, test_min)
    #   Test TEST_MAX, position 16, value of test_max variable
    stdfRecTest.assert_instance_field(inst, 16, test_max)
    #   Test TST_SUMS, position 17, value of tst_sums variable
    stdfRecTest.assert_instance_field(inst, 17, tst_sums)
    #   Test TST_SQRS, position 18, value of tst_sqrs variable
    stdfRecTest.assert_instance_field(inst, 18, tst_sqrs)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    os.remove(tf.name)

    #   Test reset method and compressed data when OPT_FLAG is used and
    #   fields after OPT_FLAG are not set

    record.reset()

    head_num = 10
    record.set_value("HEAD_NUM", head_num)
    rec_len = 1

    site_num = 11
    record.set_value("SITE_NUM", site_num)
    rec_len += 1

    test_typ = "P"
    record.set_value("TEST_TYP", test_typ)
    rec_len += 1

    test_num = 12
    record.set_value("TEST_NUM", test_num)
    rec_len += 4

    exec_cnt = 123
    record.set_value("EXEC_CNT", exec_cnt)
    rec_len += 4

    fail_cnt = 2
    record.set_value("FAIL_CNT", fail_cnt)
    rec_len += 4

    alrm_cnt = 0
    record.set_value("ALRM_CNT", alrm_cnt)
    rec_len += 4

    test_nam = "IDDQ"
    record.set_value("TEST_NAM", test_nam)
    rec_len += len(test_nam) + 1

    seq_name = "STD FLOW"
    record.set_value("SEQ_NAME", seq_name)
    rec_len += len(seq_name) + 1

    test_lbl = "label"
    record.set_value("TEST_LBL", test_lbl)
    rec_len += len(test_lbl) + 1

    expected_atdf = "TSR:"
    expected_atdf += str(head_num) + "|"
    expected_atdf += str(site_num) + "|"
    expected_atdf += str(test_num) + "|"
    expected_atdf += test_nam + "|"
    expected_atdf += test_typ + "|"
    expected_atdf += str(exec_cnt) + "|"
    expected_atdf += str(fail_cnt) + "|"
    expected_atdf += str(alrm_cnt) + "|"
    expected_atdf += seq_name + "|"
    expected_atdf += test_lbl + "|"
    expected_atdf += "||||"

    assert record.to_atdf() == expected_atdf

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 10, 30)
    #   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
    #   Test TEST_TYP, expected value test_type
    stdfRecTest.assert_char(test_typ)
    #   Test TEST_NUM, expected value test_num
    stdfRecTest.assert_int(4, test_num)
    #   Test EXEC_CNT, expected value exec_cnt
    stdfRecTest.assert_int(4, exec_cnt)
    #   Test FAIL_CNT, expected value fail_cnt
    stdfRecTest.assert_int(4, fail_cnt)
    #   Test ALRM_CNT, expected value alrm_cnt
    stdfRecTest.assert_int(4, alrm_cnt)
    #   Test TEST_NAM, expected value test_nam
    stdfRecTest.assert_ubyte(len(test_nam))
    stdfRecTest.assert_char_array(len(test_nam), test_nam)
    #   Test SEQ_NAME, expected value seq_name
    stdfRecTest.assert_ubyte(len(seq_name))
    stdfRecTest.assert_char_array(len(seq_name), seq_name)
    #   Test TEST_LBL, expected value test_lbl
    stdfRecTest.assert_ubyte(len(test_lbl))
    stdfRecTest.assert_char_array(len(test_lbl), test_lbl)

    #   ToDo: Test JSON output

    os.remove(tf.name)
