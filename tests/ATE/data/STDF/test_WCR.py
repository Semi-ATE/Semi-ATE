import os
import tempfile
import pytest

from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import WCR

#   Wafer Results Record
#   Function:
#   Contains the result information relating to each wafer tested by the job 
#   plan. TheWRRand the Wafer Information Record (WIR) bracket all the stored 
#   information pertainingto one tested wafer. This record is used only when 
#   testing at wafer probe time. AWIR/WRRpair will have the same
#   HEAD_NUM and SITE_GRP values.

def test_WCR():
    
#   ATDF page 36
    expected_atdf = "WCR:"
#   record length in bytes    
    rec_len = 0;

#   STDF page 40
    record = WCR()
    
    wafr_siz = 300.00
    record.set_value('WAFR_SIZ', wafr_siz)
    rec_len += 4;

    die_ht = 123.456
    record.set_value('DIE_HT', die_ht)
    rec_len += 4;

    die_wid = 29.12345
    record.set_value('DIE_WID', die_wid)
    rec_len += 4;

    wf_units = 4
    record.set_value('WF_UNITS', wf_units)
    rec_len += 1;

    wf_flat = 'L'
    record.set_value('WF_FLAT', wf_flat)
    rec_len += 1;
    expected_atdf += wf_flat + "|"

#    The order of fields is different in STDF and ATDF for WCR record
#    
#    STDF page 40| ATDF page 36 
#    
#    WAFR_SIZ        
#    DIE_HT    
#    DIE_WID
#    WF_UNITS       
#    WF_FLAT     = WF_FLAT
#    CENTER_X    
#    CENTER_Y    
#    POS_X       = POS_X
#    POS_Y       = POS_Y
#                  WAFR_SIZ
#                  DIE_HT
#                  DIE_WID
#                  WF_UNITS
#                  CENTER_X
#                  CENTER_Y

    center_x = -32768
    record.set_value('CENTER_X', center_x)
    rec_len += 2;

    center_y = 32767
    record.set_value('CENTER_Y', center_y)
    rec_len += 2;
    
#   ToDo check against not valid input like U/D    
    pos_x = 'L'
    record.set_value('POS_X', pos_x)
    rec_len += 1
    expected_atdf += pos_x + "|"

#   ToDo check against not valid input like L/R    
    pos_y = 'D'
    record.set_value('POS_Y', pos_y)
    rec_len += 1
    expected_atdf += pos_y + "|"

    expected_atdf += str(wafr_siz) + "|"
    expected_atdf += str(die_ht) + "|"
    expected_atdf += str(die_wid) + "|"
    expected_atdf += str(wf_units) + "|"
    expected_atdf += str(center_x) + "|"
    expected_atdf += str(center_y) 


#    Test serialization
#    1. Save WCR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 2, 30)
#   Test WAFR_SIZ, expected value wafr_siz
    stdfRecTest.assert_float(wafr_siz)
#   Test DIE_HT, expected value die_ht
    stdfRecTest.assert_float(die_ht)
#   Test DIE_WID, expected value die_wid
    stdfRecTest.assert_float(die_wid)
#   Test WF_UNITS, expected value wf_units
    stdfRecTest.assert_ubyte(wf_units)
#   Test WF_FLAT, expected value wf_flat
    stdfRecTest.assert_char(wf_flat)
#   Test CENTER_X, expected value center_x
    stdfRecTest.assert_sint(2, center_x)
#   Test CENTER_Y, expected value center_y
    stdfRecTest.assert_sint(2, center_y)
#   Test POS_X, expected value pos_x
    stdfRecTest.assert_char(pos_x)
#   Test POS_Y, expected value pos_y
    stdfRecTest.assert_char(pos_y)
          
#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = WCR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 2, 30)
#   Test WAFR_SIZ, position 3, value of wafr_siz variable
    stdfRecTest.assert_instance_field(inst, 3, wafr_siz);
#   Test DIE_HT, position 4, value of die_ht variable
    stdfRecTest.assert_instance_field(inst, 4, die_ht);
#   Test DIE_WID, position 5, value of die_wid variable
    stdfRecTest.assert_instance_field(inst, 5, die_wid);
#   Test WF_UNITS, position 6, value of wf_units variable
    stdfRecTest.assert_instance_field(inst, 6, wf_units);
#   Test WF_FLAT, position 7, value of wf_flat variable
    stdfRecTest.assert_instance_field(inst, 7, wf_flat);
#   Test CENTER_X, position 8, value of center_x variable
    stdfRecTest.assert_instance_field(inst, 8, center_x);
#   Test CENTER_Y, position 9, value of center_y variable
    stdfRecTest.assert_instance_field(inst, 9, center_y);
#   Test POS_X, position 10, value of pos_x variable
    stdfRecTest.assert_instance_field(inst, 10, pos_x);
#   Test POS_Y, position 11, value of pos_y variable
    stdfRecTest.assert_instance_field(inst, 11, pos_y);

    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output
    
    os.remove(tf.name)
