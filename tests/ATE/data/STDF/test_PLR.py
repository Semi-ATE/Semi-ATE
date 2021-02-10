import os
import io
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import PLR

#   Pin List Record
#   Function:
#   Defines the current display radix and operating mode for a pin or pin group.


def test_PLR():
    plr("<")
    plr(">")


def plr(endian):

    #   ATDF page 27
    expected_atdf = "PLR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 32
    record = PLR(endian=endian)
    grp_cnt = 3
    record.set_value("GRP_CNT", grp_cnt)
    rec_len = 2

    #    The order of fields is different in STDF and ATDF for PLR record
    #
    #    STDF page 32| ATDF page 27
    #
    #     GRP_CNT    -> missing
    #     GRP_INDX   = GRP_INDX
    #     GRP_MODE   = GRP_MODE
    #     GRP_RADX   = GRP_RADX
    #     PGM_CHAR
    #     RTN_CHAR
    #     PGM_CHAL
    #     RTN_CHAL
    #                = PGM_CHAL, PGM_CHAR
    #                = RTN_CHAL, RTN_CHAR

    grp_indx = [0, 2, 5]
    record.set_value("GRP_INDX", grp_indx)
    rec_len += len(grp_indx) * 2
    for elem in grp_indx:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1] + "|"

    grp_mode = [32, 32, 32]
    record.set_value("GRP_MODE", grp_mode)
    rec_len += len(grp_mode) * 2
    for elem in grp_mode:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1] + "|"

    grp_radx = [10, 10, 10]
    record.set_value("GRP_RADX", grp_radx)
    rec_len += len(grp_radx) * 1
    for elem in grp_radx:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1] + "|"

    pgm_char = ["1", "1", "1"]
    record.set_value("PGM_CHAR", pgm_char)
    for i in range(len(pgm_char)):
        rec_len += len(pgm_char[i]) + 1

    rtn_char = ["H", "H", "H"]
    record.set_value("RTN_CHAR", rtn_char)
    for i in range(len(rtn_char)):
        rec_len += len(rtn_char[i]) + 1

    pgm_chal = ["0", "0", "0"]
    record.set_value("PGM_CHAL", pgm_chal)
    for i in range(len(pgm_chal)):
        rec_len += len(pgm_chal[i]) + 1

    for char, chal in zip(pgm_char, pgm_chal):
        expected_atdf += char + "," + chal + "/"
    expected_atdf = expected_atdf[:-1]
    expected_atdf += "|"

    rtn_chal = ["L", "L", "L"]
    record.set_value("RTN_CHAL", rtn_chal)
    for i in range(len(rtn_chal)):
        rec_len += len(rtn_chal[i]) + 1

    for char, chal in zip(rtn_char, rtn_chal):
        expected_atdf += char + "," + chal + "/"
    expected_atdf = expected_atdf[:-1]

    #    Test serialization
    #    1. Save PLR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 63)
    #   Test GRP_CNT, expected value grp_cnt
    stdfRecTest.assert_int(2, grp_cnt)
    #   Test GRP_INDX, expected value grp_indx
    stdfRecTest.assert_int_array(2, grp_indx)
    #   Test GRP_MODE, expected value grp_mode
    stdfRecTest.assert_int_array(2, grp_mode)
    #   Test GRP_RADX, expected value grp_radx
    stdfRecTest.assert_int_array(1, grp_radx)
    #   Test PGM_CHAR, expected value pgm_char
    stdfRecTest.assert_string_array(pgm_char)
    #   Test RTN_CHAR, expected value rtn_char
    stdfRecTest.assert_string_array(rtn_char)
    #   Test PGM_CHAL, expected value pgm_chal
    stdfRecTest.assert_string_array(pgm_chal)
    #   Test RTN_CHAL, expected value rtn_chal
    stdfRecTest.assert_string_array(rtn_chal)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = PLR("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 1, 63)
    #   Test GRP_CNT, position 3, value of grp_cnt variable
    stdfRecTest.assert_instance_field(inst, 3, grp_cnt)
    #   Test GRP_INDX, position 4, value of grp_indx variable
    stdfRecTest.assert_instance_field(inst, 4, grp_indx)
    #   Test GRP_MODE, position 5, value of grp_mode variable
    stdfRecTest.assert_instance_field(inst, 5, grp_mode)
    #   Test GRP_RADX, position 6, value of grp_radx variable
    stdfRecTest.assert_instance_field(inst, 6, grp_radx)
    #   Test PGM_CHAR, position 7, value of pgm_char variable
    stdfRecTest.assert_instance_field(inst, 7, pgm_char)
    #   Test RTN_CHAR, position 8, value of rtn_char variable
    stdfRecTest.assert_instance_field(inst, 8, rtn_char)
    #   Test PGM_CHAL, position 9, value of pgm_chal variable
    stdfRecTest.assert_instance_field(inst, 9, pgm_chal)
    #   Test RTN_CHAL, position 10, value of rtn_chal variable
    stdfRecTest.assert_instance_field(inst, 10, rtn_chal)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
