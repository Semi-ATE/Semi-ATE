import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import ATR

#   Audit Trail Record
#   Function:
#   Used to record any operation that alters the contents of the STDF file.
#   The name of theprogram and all its parameters should be recorded in the
#   ASCII field provided in thisrecord. Typically, this record will be used
#   to track filter programs that have beenapplied to the data.


def test_ATR():
    atr("<")
    atr(">")


def atr(end):

    #   ATDF page 14
    expected_atdf = "ATR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 19
    record = ATR(endian=end)

    mod_time = 1609462861
    record.set_value("MOD_TIM", mod_time)
    rec_len = 4
    expected_atdf += "1:1:1 1-JAN-2021|"

    cmd_line = "modification_script.sh -src /data/stdf/2020-01-01"
    record.set_value("CMD_LINE", cmd_line)
    rec_len = 1 + len(cmd_line)
    expected_atdf += cmd_line

    #    Test serialization
    #    1. Save ATR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, endian=end)
    #   rec_len, rec_type, rec_sub
    #   rec_len = len(MOD_TIM) + 1 byte for length of cmd_line + len(cmd_line)
    rec_len = 4 + 1 + len(cmd_line)
    stdfRecTest.assert_file_record_header(rec_len, 0, 20)
    #   Test MOD_TIM, expected value mod_time
    stdfRecTest.assert_int(4, mod_time)
    #   Test CMD_LINE, first byte is length of the string:
    stdfRecTest.assert_ubyte(len(cmd_line))
    #   Test CMD_LINE, expected value
    #   "modification_script.sh -src /data/stdf/2020-01-01"
    stdfRecTest.assert_char_array(len(cmd_line), cmd_line)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = ATR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 0, 20)
    #   Test MOD_TIM field, position 3, value of mod_time variable
    stdfRecTest.assert_instance_field(inst, 3, mod_time)
    #   Test CMD_LINE field, position 4, value of cmd_line variable
    stdfRecTest.assert_instance_field(inst, 4, cmd_line)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output

    os.remove(tf.name)
