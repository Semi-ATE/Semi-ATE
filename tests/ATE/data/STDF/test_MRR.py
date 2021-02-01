import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF.MRR import MRR

#   Master Results Record
#   Function:
#   The Master Results Record (MRR) is a logical extension of the Master 
#   InformationRecord (MIR). The data can be thought of as belonging with 
#   theMIR, but it is notavailable when the tester writes theMIRinformation. 
#   Each data stream must haveexactly oneMRRas the last record in the data 
#   stream.    
def test_MRR():
    
#   ATDF page 19
    expected_atdf = "MRR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 23
    record = MRR()
    
    finish_t = 1609462861 
    record.set_value('FINISH_T', finish_t)
    rec_len = 4;
    expected_atdf += "1:1:1 1-JAN-2021|"
    
    disp_cod = 'Z'
    record.set_value('DISP_COD', disp_cod)
    rec_len += 1;
    expected_atdf += disp_cod + "|"
    
    usr_desc = 'NAS12345'
    record.set_value('USR_DESC', usr_desc)
    rec_len += 1 + len(usr_desc);
    expected_atdf += usr_desc+"|"

    exc_desc = '12345'
    record.set_value('EXC_DESC', exc_desc)
    rec_len += 1 + len(exc_desc);
    expected_atdf += exc_desc

#    Test serialization
#    1. Save MRR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 20)
#   Test FINISH_T, expected value finish_t
    stdfRecTest.assert_int(4, finish_t)
#   Test DISP_COD, expected value disp_cod
    stdfRecTest.assert_char(disp_cod)
#   Test USR_DESC, expected length of the string and value of the usr_desc
    stdfRecTest.assert_ubyte(len(usr_desc))
    stdfRecTest.assert_char_array(len(usr_desc), usr_desc);
#   Test EXC_DESC, expected length of the string and value of the usr_desc
    stdfRecTest.assert_ubyte(len(exc_desc))
    stdfRecTest.assert_char_array(len(exc_desc), exc_desc);

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = MRR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 1, 20)
#   Test FINISH_T, position 3, value of setup_t variable
    stdfRecTest.assert_instance_field(inst, 3, finish_t);
#   Test DISP_COD, position 4, value of disp_cod variable
    stdfRecTest.assert_instance_field(inst, 4, disp_cod);
#   Test USR_DESC , position 5, value of usr_desc variable
    stdfRecTest.assert_instance_field(inst, 5, usr_desc);
#   Test EXC_DESC , position 6, value of exc_desc variable
    stdfRecTest.assert_instance_field(inst, 6, exc_desc);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
