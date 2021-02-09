import os
import io
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import RDR

#   Retest Data Record
#   Function:
#   Signals that the data in this STDF file is for retested parts. The data in
#   this record,combined with information in theMIR, tells data filtering
#   programs what data toreplace when processing retest data.


def test_RDR():
    rdr("<")
    rdr(">")


def rdr(endian):

    #   ATDF page 30
    expected_atdf = "RDR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 34
    record = RDR(endian=endian)
    num_bins = 4
    record.set_value("NUM_BINS", num_bins)
    rec_len = 2

    rtst_bin = [0, 1, 2, 65535]
    record.set_value("RTST_BIN", rtst_bin)
    rec_len += len(rtst_bin) * 2
    for elem in rtst_bin:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1]

    #    Test serialization
    #    1. Save RDR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 70)
    #   Test NUM_BINS, expected value num_bins
    stdfRecTest.assert_int(2, num_bins)
    #   Test RTST_BIN, expected value rtst_bin
    stdfRecTest.assert_int_array(2, rtst_bin)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = RDR("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 1, 70)
    #   Test NUM_BINS, position 3, value of num_bins variable
    stdfRecTest.assert_instance_field(inst, 3, num_bins)
    #   Test RTST_BIN, position 4, value of rtst_bin variable
    stdfRecTest.assert_instance_field(inst, 4, rtst_bin)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
