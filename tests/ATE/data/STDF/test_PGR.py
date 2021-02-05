import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import PGR

#   Pin Group Record
#   Function:
#   Associates a name with a group of pins 
def test_PGR():
    
#   ATDF page 26
    expected_atdf = "PGR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 31
    record = PGR()

    grp_indx = 32768
    record.set_value('GRP_INDX', grp_indx)
    rec_len = 2;
    expected_atdf += str(grp_indx) + "|"
    
    grp_nam = 'gVdd'
    record.set_value('GRP_NAM', grp_nam)
    rec_len += len(grp_nam) + 1;
    expected_atdf += str(grp_nam) + "|"

    indx_cnt = 3
    record.set_value('INDX_CNT', indx_cnt)
    rec_len += 2;
    
    pmr_indx = [0, 255, 65535]
    record.set_value('PMR_INDX', pmr_indx)
    rec_len += indx_cnt*2;
    for elem in pmr_indx:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1]


#    Test serialization
#    1. Save PGR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 62)
#   Test GRP_INDX, expected value grp_indx
    stdfRecTest.assert_int(2, grp_indx)
#   Test GRP_NAM, expected value grp_nam
    stdfRecTest.assert_ubyte(len(grp_nam))
    stdfRecTest.assert_char_array(len(grp_nam), grp_nam)
#   Test INDX_CNT, expected value indx_cnt
    stdfRecTest.assert_int(2, indx_cnt)
#   Test PMR_CNT, expected value pmr_indx
    stdfRecTest.assert_int_array(2, pmr_indx)
    

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = PGR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 1, 62)
#   Test GRP_INDX, position 3, value of grp_indx variable
    stdfRecTest.assert_instance_field(inst, 3, grp_indx);
#   Test GRP_NAM, position 4, value of grp_nam variable
    stdfRecTest.assert_instance_field(inst, 4, grp_nam);
#   Test INDX_CNT, position 5, value of indx_cnt variable
    stdfRecTest.assert_instance_field(inst, 5, indx_cnt);
#   Test PMR_INDX, position 6, value of pmr_indx variable
    stdfRecTest.assert_instance_field(inst, 6, pmr_indx);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
