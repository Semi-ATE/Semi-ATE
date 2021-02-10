import os
import io
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF.PCR import PCR

#   Part Count Record
#   Function:
#   Contains the part count totals for one or all test sites. Each data
#   stream must have atleast onePCRto show the part count


def test_PCR():
    pcr("<")
    pcr(">")


def pcr(endian):

    #   ATDF page 20
    expected_atdf = "PCR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 24
    record = PCR(endian=endian)

    head_num = 1
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_num = 1
    record.set_value("SITE_NUM", site_num)
    rec_len += 1
    expected_atdf += str(site_num) + "|"

    part_cnt = 4294967295
    record.set_value("PART_CNT", part_cnt)
    rec_len += 4
    expected_atdf += str(part_cnt) + "|"

    rtst_cnt = 123
    record.set_value("RTST_CNT", rtst_cnt)
    rec_len += 4
    expected_atdf += str(rtst_cnt) + "|"

    abrt_cnt = 0
    record.set_value("ABRT_CNT", abrt_cnt)
    rec_len += 4
    expected_atdf += str(abrt_cnt) + "|"

    good_cnt = 4294967172
    record.set_value("GOOD_CNT", good_cnt)
    rec_len += 4
    expected_atdf += str(good_cnt) + "|"

    func_cnt = 0
    record.set_value("FUNC_CNT", func_cnt)
    rec_len += 4
    expected_atdf += str(func_cnt)

    #    Test serialization
    #    1. Save PCR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 30)
    #   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
    #   Test PART_CNT, expected value part_cnt
    stdfRecTest.assert_int(4, part_cnt)
    #   Test RTST_CNT, expected value rtst_cnt
    stdfRecTest.assert_int(4, rtst_cnt)
    #   Test ABRT_CNT, expected value abrt_cnt
    stdfRecTest.assert_int(4, abrt_cnt)
    #   Test GOOD_CNT, expected value good_cnt
    stdfRecTest.assert_int(4, good_cnt)
    #   Test FUNC_CNT, expected value func_cnt
    stdfRecTest.assert_int(4, func_cnt)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value
    #
    #    ToDo : make test with both endianness

    inst = PCR("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 1, 30)
    #   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num)
    #   Test SITE_NUM, position 4, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 4, site_num)
    #   Test PART_CNT, position 5, value of part_cnt variable
    stdfRecTest.assert_instance_field(inst, 5, part_cnt)
    #   Test RTST_CNT, position 6, value of rtst_cnt variable
    stdfRecTest.assert_instance_field(inst, 6, rtst_cnt)
    #   Test ABRT_CNT, position 7, value of abrt_cnt variable
    stdfRecTest.assert_instance_field(inst, 7, abrt_cnt)
    #   Test GOOD_CNT, position 8, value of good_cnt variable
    stdfRecTest.assert_instance_field(inst, 8, good_cnt)
    #   Test FUNC_CNT, position 9, value of func_cnt variable
    stdfRecTest.assert_instance_field(inst, 9, func_cnt)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
