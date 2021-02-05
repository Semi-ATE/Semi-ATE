import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import HBR

#   Hardware Bin Record
#   Function:
#   Stores a count of the parts “physically” placed in a particular bin after 
#   testing. (Inwafer testing, “physical” binning is not an actual transfer of 
#   the chip, but rather isrepresented by a drop of ink or an entry in a wafer 
#   map file.) This bin count can be fora single test site (when parallel 
#   testing) or a total for all test sites. The STDFspecification also 
#   supports a Software Bin Record (SBR) for logical binning categories.
#   A part is “physically” placed in a hardware bin after testing. A part can 
#   be “logically”associated with a software bin during or after testing.

def test_HBR():
    hbr('<')
    hbr('>')

def hbr(end):
    
#   ATDF page 21
    expected_atdf = "HBR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 25
    record = HBR(endian = end)
    
    head_num = 255
    record.set_value('HEAD_NUM', head_num)
    rec_len = 1;
    expected_atdf += str(head_num)+"|"
    
    site_num = 255
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"
    
    hbin_num = 32767
    record.set_value('HBIN_NUM', hbin_num)
    rec_len += 2;
    expected_atdf += str(hbin_num) + "|"

    hbin_cnt = 4294967295
    record.set_value('HBIN_CNT', hbin_cnt)
    rec_len += 4;
    expected_atdf += str(hbin_cnt) + "|"

    hbin_pf = 'F'
    record.set_value('HBIN_PF', hbin_pf)
    rec_len += 1;
    expected_atdf += str(hbin_pf) + "|"

    hbin_nam = 'FAIL'
    record.set_value('HBIN_NAM', hbin_nam)
    rec_len += len(hbin_nam) + 1;
    expected_atdf += str(hbin_nam)

#    Test serialization
#    1. Save EPS STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, end)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 40)
#   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
#   Test HBIN_NUM, expected value hbin_num
    stdfRecTest.assert_int(2, hbin_num)
#   Test HBIN_CNT, expected value hbin_cnt
    stdfRecTest.assert_int(4, hbin_cnt)
#   Test HBIN_PF, expected value hbin_pf
    stdfRecTest.assert_char(hbin_pf)
#   Test HBIN_NAM, expected value hbin_nam
    stdfRecTest.assert_ubyte(len(hbin_nam))
    stdfRecTest.assert_char_array(len(hbin_nam), hbin_nam)

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value

    inst = HBR('V4', end, w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 1, 40)
#   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num);
#   Test SITE_NUM, position 4, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 4, site_num);
#   Test HBIN_NUM, position 5, value of hbin_num variable
    stdfRecTest.assert_instance_field(inst, 5, hbin_num);
#   Test HBIN_CNT, position 6, value of hbin_cnt variable
    stdfRecTest.assert_instance_field(inst, 6, hbin_cnt);
#   Test HBIN_PF, position 7, value of hbin_pf variable
    stdfRecTest.assert_instance_field(inst, 7, hbin_pf);
#   Test HBIN_NAM, position 8, value of hbin_nam variable
    stdfRecTest.assert_instance_field(inst, 8, hbin_nam);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
