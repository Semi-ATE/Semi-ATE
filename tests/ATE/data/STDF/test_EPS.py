import os
import io
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import EPS

#   End Program Section Record
#   Function:
#   Marks the end of the current program section (or sequencer) in the job plan.


def test_EPS():
    eps("<")
    eps(">")


def eps(endian):

    #   ATDF page 58
    expected_atdf = "EPS:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 63
    record = EPS(endian=endian)

    #    Test serialization
    #    1. Save EPS STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 20, 20)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = EPS("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 20, 20)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
