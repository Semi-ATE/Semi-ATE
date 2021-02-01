import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF.PMR import PMR

#   Pin Map Record
#   Function:
#   Provides indexing of tester channel names, and maps them to physical and 
#   logical pinnames. EachPMRdefines the information for a single channel/pin 
#   combination.
def test_PMR():
    
#   ATDF page 24
    expected_atdf = "PMR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 29
    record = PMR()
    pmr_indx = 32767
    record.set_value('PMR_INDX', pmr_indx)
    rec_len = 2;
    expected_atdf += str(pmr_indx) + "|"
    
    chan_typ = 65535
    record.set_value('CHAN_TYP', chan_typ)
    rec_len += 2;
    expected_atdf += str(chan_typ) + "|"
    
    chan_nam = 'Vdd'
    record.set_value('CHAN_NAM', chan_nam)
    rec_len += len(chan_nam) + 1;
    expected_atdf += str(chan_nam) + "|"

    phy_nam = 'PWR_Supp_ch16'
    record.set_value('PHY_NAM', phy_nam)
    rec_len += len(phy_nam) + 1;
    expected_atdf += str(phy_nam) + "|"

    log_nam = 'Vdd5V'
    record.set_value('LOG_NAM', log_nam)
    rec_len += len(log_nam)+1;
    expected_atdf += str(log_nam) + "|"

    head_num = 128
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) + "|"
    
    site_num = 128
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num)


#    Test serialization
#    1. Save PMR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 60)
#   Test PMR_INDX, expected value pmr_indx
    stdfRecTest.assert_int(2, pmr_indx)
#   Test CHAN_TYP, expected value chan_typ
    stdfRecTest.assert_int(2, chan_typ)
#   Test CHAN_NAM, expected value chan_nam
    stdfRecTest.assert_ubyte(len(chan_nam))
    stdfRecTest.assert_char_array(len(chan_nam), chan_nam)
#   Test PHY_NAM, expected value phy_nam
    stdfRecTest.assert_ubyte(len(phy_nam))
    stdfRecTest.assert_char_array(len(phy_nam), phy_nam)
#   Test LOG_NAM, expected value log_nam
    stdfRecTest.assert_ubyte(len(log_nam))
    stdfRecTest.assert_char_array(len(log_nam), log_nam)
#   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = PMR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 1, 60)
#   Test PMR_INDX, position 3, value of pmr_indx variable
    stdfRecTest.assert_instance_field(inst, 3, pmr_indx);
#   Test CHAN_TYP, position 4, value of chan_typ variable
    stdfRecTest.assert_instance_field(inst, 4, chan_typ);
#   Test CHAN_NAM, position 5, value of chan_nam variable
    stdfRecTest.assert_instance_field(inst, 5, chan_nam);
#   Test PHY_NAM, position 6, value of phy_nam variable
    stdfRecTest.assert_instance_field(inst, 6, phy_nam);
#   Test LOG_NAM, position 7, value of log_nam variable
    stdfRecTest.assert_instance_field(inst, 7, log_nam)
#   Test HEAD_NUM, position 8, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 8, head_num);
#   Test SITE_NUM, position 9, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 9, site_num);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
