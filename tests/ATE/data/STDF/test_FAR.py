import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import FAR

#   File Attributes Record
#   Functuion:
#   Contains the information necessary to determine
#   how to decode the STDF datacontained in the file.


def test_FAR():
    far("<")
    far(">")


def far(end):

    #   STDF v4 page 57
    record = FAR(endian=end)

    #    Test serialization
    #    1. Save FAR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(2, 0, 10)
    #   Test REC_CPU, expected value 2
    stdfRecTest.assert_ubyte(2)
    #   Test STDF_VER, expected value 4
    stdfRecTest.assert_ubyte(4)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = FAR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, 2, 0, 10)
    #   Test REC_CPU field, position 3, value 2
    stdfRecTest.assert_instance_field(inst, 3, 2)
    #   Test STDF_VER field, position 4, value 4
    stdfRecTest.assert_instance_field(inst, 4, 4)

    #   Test ATDF output
    expected_atdf = "FAR:A|4|2|U"
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
    os.remove(tf.name)
