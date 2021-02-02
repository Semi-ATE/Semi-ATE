import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import BPS

#   Begin Program Section Record
#   Function:
#   Marks the beginning of a new program section (or sequencer) in the job plan.

def test_BPS():
    
#   ATDF page 57
    expected_atdf = "BPS:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 62
    record = BPS()

    seq_name = 'DC_TESTS'
    record.set_value('SEQ_NAME', seq_name)
    rec_len += len(seq_name) + 1;
    expected_atdf += str(seq_name)

#    Test serialization
#    1. Save BPS STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")
#  ERROR  : ATE.data.STDF.records.STDFError: EPS._pack_item(REC_LEN) : Unsupported Reference '' vs 'U*2'
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 20, 10)
#   Test SEQ_NAME, expected value seq_name
    stdfRecTest.assert_ubyte(len(seq_name))
    stdfRecTest.assert_char_array(len(seq_name), seq_name)

    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = BPS('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 20, 10)
#   Test SEQ_NAME, position 3, value of grp_nam variable
    stdfRecTest.assert_instance_field(inst, 3, seq_name);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
