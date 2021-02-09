import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import WIR

#   Wafer Information Record
#   Function:
#   Acts mainly as a marker to indicate where testing of a particular wafer
#   begins for eachwafer tested by the job plan. TheWIRand the Wafer Results
#   Record (WRR) bracket allthe stored information pertaining to one tested
#   wafer. This record is used only whentesting at wafer probe. AWIR/WRRpair
#   will have the sameHEAD_NUMandSITE_GRPvalues.


def test_WIR():
    wir("<")
    wir(">")


def wir(end):

    #   ATDF page 33
    expected_atdf = "WIR:"
    #   record length in bytes
    rec_len = 0

    #   STDF v4 page 37
    record = WIR(endian=end)

    head_num = 1
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_grp = 1
    record.set_value("SITE_GRP", site_grp)
    rec_len += 1

    start_t = 1609462861
    record.set_value("START_T", start_t)
    rec_len += 4
    expected_atdf += "1:1:1 1-JAN-2021|"

    #    The order of fields is different in STDF and ATDF for WIR record
    #    STDF page 37, the order is HEAD_NUM, SITE_GRP, START_T,  WAFER_ID
    #    ATDF page 33, the order is HEAD_NUM, START_T,  SITE_GRP, WAFER_ID

    expected_atdf += str(site_grp) + "|"

    wafer_id = "WFR_NAS9999"
    record.set_value("WAFER_ID", wafer_id)
    rec_len += len(wafer_id) + 1
    expected_atdf += wafer_id

    #    Test serialization
    #    1. Save WIR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    tf = tempfile.NamedTemporaryFile(delete=False)

    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")

    stdfRecTest = STDFRecordTest(f, end)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 2, 10)
    #   Test HEAD_NUM, expected value num_bins
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_GRP, expected value site_grp
    stdfRecTest.assert_int(1, site_grp)
    #   Test START_T, expected value start_t
    stdfRecTest.assert_int(4, start_t)
    #   Test WAFER_ID, expected value site_cnt
    stdfRecTest.assert_ubyte(len(wafer_id))
    stdfRecTest.assert_char_array(len(wafer_id), wafer_id)

    f.close()

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = WIR("V4", end, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 2, 10)
    #   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num)
    #   Test SITE_GRP, position 4, value of site_grp variable
    stdfRecTest.assert_instance_field(inst, 4, site_grp)
    #   Test START_T, position 5, value of start_t variable
    stdfRecTest.assert_instance_field(inst, 5, start_t)
    #   Test WAFER_ID, position 6, value of wafer_id variable
    stdfRecTest.assert_instance_field(inst, 6, wafer_id)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output

    os.remove(tf.name)
