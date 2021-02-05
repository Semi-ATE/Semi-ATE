import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import SBR

#   Software Bin Record
#   Function:
#   Stores a count of the parts associated with a particular logical bin after
#   testing. Thisbin count can be for a single test site (when parallel 
#   testing) or a total for all test sites.The STDF specification also 
#   supports a Hardware Bin Record (HBR) for actual physical binning. A part 
#   is “physically” placed in a hardware bin after testing. A part can be
#   “logically” associated with a software bin during or after testing.
def test_SBR():
    sbr('<')
    sbr('>')

def sbr(end):
    
#   ATDF page 23
    expected_atdf = "SBR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 27
    record = SBR(endian = end)
    head_num = 255
    record.set_value('HEAD_NUM', head_num)
    rec_len = 1;
    expected_atdf += str(head_num) + "|"
    
    site_num = 255
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"
    
    sbin_num = 1000
    record.set_value('SBIN_NUM', sbin_num)
    rec_len += 2;
    expected_atdf += str(sbin_num) + "|"

    sbin_cnt = 1000000
    record.set_value('SBIN_CNT', sbin_cnt)
    rec_len += 4;
    expected_atdf += str(sbin_cnt) + "|"

    sbin_pf = 'F'
    record.set_value('SBIN_PF', sbin_pf)
    rec_len += 1;
    expected_atdf += str(sbin_pf) + "|"

    sbin_nam = 'FAIL_IDDQ'
    record.set_value('SBIN_NAM', sbin_nam)
    rec_len += len(sbin_nam) + 1;
    expected_atdf += str(sbin_nam)

#    Test serialization
#    1. Save SBR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, end)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 50)
#   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
#   Test SHBIN_NUM, expected value sbin_num
    stdfRecTest.assert_int(2, sbin_num)
#   Test SBIN_CNT, expected value sbin_cnt
    stdfRecTest.assert_int(4, sbin_cnt)
#   Test SBIN_PF, expected value sbin_pf
    stdfRecTest.assert_char(sbin_pf)
#   Test SBIN_NAM, expected value sbin_nam
    stdfRecTest.assert_ubyte(len(sbin_nam))
    stdfRecTest.assert_char_array(len(sbin_nam), sbin_nam)

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value

    inst = SBR('V4', end, w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 1, 50)
#   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num);
#   Test SITE_NUM, position 4, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 4, site_num);
#   Test SBIN_NUM, position 5, value of sbin_num variable
    stdfRecTest.assert_instance_field(inst, 5, sbin_num);
#   Test SBIN_CNT, position 6, value of sbin_cnt variable
    stdfRecTest.assert_instance_field(inst, 6, sbin_cnt);
#   Test SBIN_PF, position 7, value of sbin_pf variable
    stdfRecTest.assert_instance_field(inst, 7, sbin_pf);
#   Test SBIN_NAM, position 8, value of sbin_nam variable
    stdfRecTest.assert_instance_field(inst, 8, sbin_nam);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
