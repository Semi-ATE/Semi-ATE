import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import PRR

#   Part Results Record
#   Function:
#   Contains the result information relating to each part tested by the test
#   program. ThePRRand the Part Information Record (PIR) bracket all the
#   stored informationpertaining to one tested part.


def test_PRR():
    prr("<")
    prr(">")


def prr(end):

    #   ATDF page 39
    expected_atdf = "PRR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 43
    record = PRR(endian=end)

    head_num = 1
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_num = 1
    record.set_value("SITE_NUM", site_num)
    rec_len += 1
    expected_atdf += str(site_num) + "|"

    """
    The order of fields is different in STDF and ATDF for PRR record
    
    STDF page 43| ATDF page 39
    
     HEAD_NUM    = HEAD_NUM    
     SITE_NUM    = SITE_NUM  
     PART_FLG    
     NUM_TEST        
     HARD_BIN       
     SOFT_BIN       
     X_COORD       
     Y_COORD       
     TEST_T       
     PART_ID     = PART_ID
                   NUM_TEST
                   PART_FLG bits 3 & 4
                   HARD_BIN
                   SOFT_BIN
                   X_COORD
                   Y_COORD
                   PART_FLG bit 0 or 1
                   PART_FLG bit 2
                   TEST_T
     PART_TXT    = PART_TXT
     PART_FIX    = PART_FIX

    """

    part_flg = ["1", "0", "1", "1", "0", "0", "0", "0"]
    record.set_value("PART_FLG", part_flg)
    rec_len += 1

    num_test = 23
    record.set_value("NUM_TEST", num_test)
    rec_len += 2

    hard_bin = 1
    record.set_value("HARD_BIN", hard_bin)
    rec_len += 2

    soft_bin = 32767
    record.set_value("SOFT_BIN", soft_bin)
    rec_len += 2

    x_coord = 2002
    record.set_value("X_COORD", x_coord)
    rec_len += 2

    y_coord = 1001
    record.set_value("Y_COORD", y_coord)
    rec_len += 2

    test_t = 4236
    record.set_value("TEST_T", test_t)
    rec_len += 4

    part_id = "NAS4017"
    record.set_value("PART_ID", part_id)
    rec_len += len(part_id) + 1

    expected_atdf += str(part_id) + "|"
    expected_atdf += str(num_test) + "|"
    #                   PART_FLG bits 3 & 4
    expected_atdf += "F" + "|"
    expected_atdf += str(hard_bin) + "|"
    expected_atdf += str(soft_bin) + "|"
    expected_atdf += str(x_coord) + "|"
    expected_atdf += str(y_coord) + "|"
    #                   PART_FLG bit 0 or 1
    expected_atdf += "I" + "|"
    #                   PART_FLG bit 2
    expected_atdf += "Y" + "|"
    expected_atdf += str(test_t) + "|"

    part_txt = "SENSOR"
    record.set_value("PART_TXT", part_txt)
    rec_len += len(part_txt) + 1
    expected_atdf += str(part_txt) + "|"

    #   Passing array of bits (as string) values does not work. May be the problem
    #   is in the file records.py, line 675 or 1157
    #   Using as expected value for the comparission below
    part_fix_expected = [
        "1",
        "0",
        "1",
        "1",
        "0",
        "1",
        "0",
        "0",
        "0",
        "1",
        "0",
        "0",
        "1",
        "0",
        "1",
        "1",
    ]
    #   Only the array with int values is working so far
    part_fix = [45, 210, 45, 210]
    record.set_value("PART_FIX", part_fix)
    #   One byte for length and 2 bytes data
    rec_len += 1 + 4
    #   hex representation of the part_fix list
    expected_atdf += "2DD22DD2"

    #    Test serialization
    #    1. Save PRR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")
    #  seimit found ERROR  : ATE.data.STDF.records.STDFError: EPS._pack_item(REC_LEN) : Unsupported Reference '' vs 'U*2'
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 5, 20)
    #   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
    #   Test PART_FLG, expected value part_flg
    stdfRecTest.assert_bits(part_flg)
    #   Test NUM_TEST, expected value num_test
    stdfRecTest.assert_int(2, num_test)
    #   Test HARD_BIN, expected value hard_bin
    stdfRecTest.assert_int(2, hard_bin)
    #   Test SOFT_BIN, expected value soft_bin
    stdfRecTest.assert_int(2, soft_bin)
    #   Test X_COORD, expected value x_coord
    stdfRecTest.assert_sint(2, x_coord)
    #   Test Y_COORD, expected value y_coord
    stdfRecTest.assert_sint(2, y_coord)
    #   Test TEST_T, expected value test_t
    stdfRecTest.assert_int(4, test_t)
    #   Test PART_ID, expected value part_id
    stdfRecTest.assert_ubyte(len(part_id))
    stdfRecTest.assert_char_array(len(part_id), part_id)
    #   Test PART_TXT, expected value part_txt
    stdfRecTest.assert_ubyte(len(part_txt))
    stdfRecTest.assert_char_array(len(part_txt), part_txt)
    #   Test PART_FIX, expected value part_fix
    stdfRecTest.assert_ubyte(4)
    stdfRecTest.assert_ubyte(0x2D)
    stdfRecTest.assert_ubyte(0xD2)
    stdfRecTest.assert_ubyte(0x2D)
    stdfRecTest.assert_ubyte(0xD2)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = PRR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 5, 20)
    #   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num)
    #   Test SITE_NUM, position 4, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 4, site_num)
    #   Test PART_FLG, position 5, value of part_flg variable
    stdfRecTest.assert_instance_field(inst, 5, part_flg)
    #   Test NUM_TEST, position 6, value of num_test variable
    stdfRecTest.assert_instance_field(inst, 6, num_test)
    #   Test HARD_BIN, position 7, value of hard_bin variable
    stdfRecTest.assert_instance_field(inst, 7, hard_bin)
    #   Test SOFT_BIN, position 8, value of hard_bin variable
    stdfRecTest.assert_instance_field(inst, 8, soft_bin)
    #   Test X_COORD, position 9, value of x_coord variable
    stdfRecTest.assert_instance_field(inst, 9, x_coord)
    #   Test Y_COORD, position 10, value of y_coord variable
    stdfRecTest.assert_instance_field(inst, 10, y_coord)
    #   Test TEST_T, position 11, value of test_t variable
    stdfRecTest.assert_instance_field(inst, 11, test_t)
    #   Test PART_ID, position 12, value of part_id variable
    stdfRecTest.assert_instance_field(inst, 12, part_id)
    #   Test PART_TXT, position 13, value of part_txt variable
    stdfRecTest.assert_instance_field(inst, 13, part_txt)
    #   Test PART_FIX, position 14, value of part_fix variable
    stdfRecTest.assert_instance_field(inst, 14, part_fix_expected)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output

    os.remove(tf.name)
