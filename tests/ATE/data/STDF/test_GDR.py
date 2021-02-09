import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import GDR

#   Generic Data Record
#   Function:
#   Contains information that does not conform to any other record type defined
#   by theSTDF specification. Such records are intended to be written under the
#   control of jobplans executing on the tester. This data may be used for any
#   purpose that the userdesires.


def test_GDR():
    gdr("<")
    gdr(">")


def gdr(end):

    #   ATDF page 59
    expected_atdf = "GDR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 64
    record = GDR(endian=end)

    fld_cnt = 12
    record.set_value("FLD_CNT", fld_cnt)
    rec_len += 2

    gen_data = [(1, 255)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for code + 1 byte for data U*1
    rec_len += 2
    expected_atdf += "U255|"

    gen_data = [(2, 65535)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 2 byte for data U*2
    rec_len += 4
    expected_atdf += "M65535|"

    gen_data = [(3, 4294967295)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 4 byte for data U*4
    rec_len += 6
    expected_atdf += "B4294967295|"

    gen_data = [(4, -128)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for code + 1 byte for data I*1
    rec_len += 2
    expected_atdf += "I-128|"

    gen_data = [(5, -32768)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 2 byte for data I*2
    rec_len += 4
    expected_atdf += "S-32768|"

    gen_data = [(6, -2147483648)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 4 byte for data I*4
    rec_len += 6
    expected_atdf += "L-2147483648|"

    gen_data = [(7, 123.4567)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 4 byte for data R*4
    rec_len += 6
    expected_atdf += "F123.4567|"

    gen_data = [(8, -123.456789012345)]
    record.set_value("GEN_DATA", gen_data)
    # 1 byte for padding + 1 byte for code + 8 byte for data R*8
    rec_len += 10
    expected_atdf += "D-123.456789012345|"

    gen_data = [(10, "ASCII Text")]
    record.set_value("GEN_DATA", gen_data)
    # 1 for code, 1 for length, 10 for data
    rec_len += 12
    expected_atdf += "TASCII Text|"

    gen_data = [(11, "Binary Text")]
    record.set_value("GEN_DATA", gen_data)
    # 1 for code, 1 for length, 11 for data
    rec_len += 13
    expected_atdf += "X42696E6172792054657874|"

    gen_data = [(12, ["1", "1", "0", "1", "1", "1", "1", "0", "1", "0", "1", "1"])]
    record.set_value("GEN_DATA", gen_data)
    # 1 for code, 2 for length, 2 for data
    rec_len += 5
    expected_atdf += "Y7B0D|"

    gen_data = [(13, [15, 8])]
    record.set_value("GEN_DATA", gen_data)
    # 1 for code, 1 for length, 2 for data
    rec_len += 2
    expected_atdf += "N15,8"

    #    Test serialization
    #    1. Save GDR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 50, 10)
    #   Test FLD_CNT, expected value fld_cnt
    stdfRecTest.assert_int(2, fld_cnt)
    #    gen_data = [ (1, 255)]
    stdfRecTest.assert_int(1, 1)
    stdfRecTest.assert_int(1, 255)
    #    gen_data = [ (2, 65535)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 2)
    #   value
    stdfRecTest.assert_int(2, 65535)
    #    gen_data = [ (3, 4294967295)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 3)
    #   value
    stdfRecTest.assert_int(4, 4294967295)

    #    gen_data = [ (4, -128)]
    stdfRecTest.assert_int(1, 4)
    stdfRecTest.assert_sint(1, -128)

    #    gen_data = [ (5, -32768)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 5)
    #   value
    stdfRecTest.assert_sint(2, -32768)

    #    gen_data = [ (6,-2147483648)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 6)
    #   value
    stdfRecTest.assert_sint(4, -2147483648)

    #    gen_data = [ (7, 123.4567)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 7)
    #   value
    stdfRecTest.assert_float(123.4567)

    #    gen_data = [ (8, -123.456789012345)]
    #   padding
    stdfRecTest.assert_int(1, 0)
    #   code
    stdfRecTest.assert_int(1, 8)
    #   value
    stdfRecTest.assert_double(-123.456789012345)

    #    gen_data = [ (10, "ASCII Text")]
    #   code
    stdfRecTest.assert_int(1, 10)
    #   length
    stdfRecTest.assert_int(1, 10)
    #   value
    stdfRecTest.assert_char_array(10, "ASCII Text")

    #    gen_data = [ (11, "Binary Text")]
    #   code
    stdfRecTest.assert_int(1, 11)
    #   length
    stdfRecTest.assert_int(1, 11)
    #   value
    stdfRecTest.assert_char_array(11, "Binary Text")

    #    gen_data = [ (12, ['1', '1', '0', '1', '1', '1', '1', '0', '1', '0', '1', '1'])]
    #   code
    stdfRecTest.assert_int(1, 12)
    #   length in bits
    stdfRecTest.assert_int(2, 12)
    #   value
    stdfRecTest.assert_int(1, 0x7B)
    stdfRecTest.assert_int(1, 0x0D)

    #    gen_data = [ (13, [15, 8])]
    #   code
    stdfRecTest.assert_int(1, 13)
    #   value 15 8 => 8F (First item in low 4 bits, second item in high 4 bits.)
    stdfRecTest.assert_int(1, 0x8F)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = GDR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 50, 10)
    #   Test FLD_CNT, position 3, value of fld_cnt variable
    stdfRecTest.assert_instance_field(inst, 3, fld_cnt)
    # ToDo make check for instances!

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output

    os.remove(tf.name)
