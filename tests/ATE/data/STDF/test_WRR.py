import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import WRR

#   Wafer Results Record
#   Function:
#   Contains the result information relating to each wafer tested by the job 
#   plan. TheWRRand the Wafer Information Record (WIR) bracket all the stored 
#   information pertainingto one tested wafer. This record is used only when 
#   testing at wafer probe time. AWIR/WRRpair will have the same
#   HEAD_NUM and SITE_GRP values.

def test_WRR():
    
#   ATDF page 34
    expected_atdf = "WRR:"
#   record length in bytes    
    rec_len = 0;

#   STDF page 38
    record = WRR()
    
    head_num = 1
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) + "|"

    site_grp = 1
    record.set_value('SITE_GRP', site_grp)
    rec_len += 1;

    finish_t = 1609462861 
    record.set_value('FINISH_T', finish_t)
    rec_len += 4;
    expected_atdf += "1:1:1 1-JAN-2021|"

#    The order of fields is different in STDF and ATDF for WRR record
#    
#    STDF page 38| ATDF page 34 
#    
#    HEAD_NUM    = HEAD_NUM
#    SITE_GRP    
#    FINISH_T    = FINISH_T
#    PART_CNT    = PART_CNT   
#                | WAFER_ID
#                | SITE_GRP
#    RTST_CNT    = RTST_CNT
#    ABRT_CNT    = ABRT_CNT
#    GOOD_CNT    = GOOD_CNT
#    FUNC_CNT    = FUNC_CNT
#    WAFER_ID    
#    FABWF_ID    = FABWF_ID
#    FRAME_ID    = FRAME_ID
#    MASK_ID     = MASK_ID
#    USR_DESC    = USR_DESC
#    EXC_DESC    = EXC_DESC

    part_cnt = 11234567 
    record.set_value('PART_CNT', part_cnt)
    rec_len += 4;
    expected_atdf += str(part_cnt) + "|"

    rtst_cnt = 123 
    record.set_value('RTST_CNT', rtst_cnt)
    rec_len += 4;

    abrt_cnt = 0 
    record.set_value('ABRT_CNT', abrt_cnt)
    rec_len += 4;

    good_cnt = 11234444
    record.set_value('GOOD_CNT', good_cnt)
    rec_len += 4;

    func_cnt = 0
    record.set_value('FUNC_CNT', func_cnt)
    rec_len += 4;

    wafer_id = 'WFR_NAS9999'
    record.set_value('WAFER_ID', wafer_id)
    rec_len += len(wafer_id) + 1;
    expected_atdf += wafer_id + "|"
    
    expected_atdf += str(site_grp) + "|"
    expected_atdf += str(rtst_cnt) + "|"
    expected_atdf += str(abrt_cnt) + "|"
    expected_atdf += str(good_cnt) + "|"
    expected_atdf += str(func_cnt) + "|"

    fabwf_id = 'FABWFR_FR'
    record.set_value('FABWF_ID', fabwf_id)
    rec_len += len(fabwf_id) + 1;
    expected_atdf += fabwf_id + "|"

    frame_id = 'FRAME_213141'
    record.set_value('FRAME_ID', frame_id)
    rec_len += len(frame_id) + 1;
    expected_atdf += frame_id + "|"

    mask_id = 'MASK_131212'
    record.set_value('MASK_ID', mask_id)
    rec_len += len(mask_id) + 1;
    expected_atdf += mask_id + "|"

    usr_desc = 'USR_DESC'
    record.set_value('USR_DESC', usr_desc)
    rec_len += len(usr_desc) + 1;
    expected_atdf += usr_desc + "|"

    exc_desc = 'DESC_NOTHING'
    record.set_value('EXC_DESC', exc_desc)
    rec_len += len(exc_desc) + 1;
    expected_atdf += exc_desc

#    Test serialization
#    1. Save WRR STDF record into a file
#    2. Read byte by byte and compare with expected value
    
    tf = tempfile.NamedTemporaryFile(delete=False)  
    
    f = open(tf.name, "wb")

    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 2, 20)
#   Test HEAD_NUM, expected value num_bins
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_GRP, expected value site_grp
    stdfRecTest.assert_int(1, site_grp)
#   Test FINISH_T, expected value finish_t
    stdfRecTest.assert_int(4, finish_t)
#   Test PART_CNT, expected value part_cnt
    stdfRecTest.assert_int(4, part_cnt)
#   Test RTST_CNT, expected value rtst_cnt
    stdfRecTest.assert_int(4, rtst_cnt)
#   Test ABRT_CNT, expected value abrt_cnt
    stdfRecTest.assert_int(4, abrt_cnt)
#   Test GOOD_CNT, expected value good_cnt
    stdfRecTest.assert_int(4, good_cnt)
#   Test FUNC_CNT, expected value func_cnt
    stdfRecTest.assert_int(4, func_cnt)
#   Test WAFER_ID, expected value wafer_id
    stdfRecTest.assert_ubyte(len(wafer_id))
    stdfRecTest.assert_char_array(len(wafer_id), wafer_id);
#   Test FABWF_ID, expected value fabwf_id
    stdfRecTest.assert_ubyte(len(fabwf_id))
    stdfRecTest.assert_char_array(len(fabwf_id), fabwf_id);
#   Test FRAME_ID, expected value frame_id
    stdfRecTest.assert_ubyte(len(frame_id))
    stdfRecTest.assert_char_array(len(frame_id), frame_id);
#   Test MASK_ID, expected value mask_id
    stdfRecTest.assert_ubyte(len(mask_id))
    stdfRecTest.assert_char_array(len(mask_id), mask_id);
#   Test USR_DESC, expected value usr_desc
    stdfRecTest.assert_ubyte(len(usr_desc))
    stdfRecTest.assert_char_array(len(usr_desc), usr_desc);
#   Test EXC_DESC, expected value exc_desc
    stdfRecTest.assert_ubyte(len(exc_desc))
    stdfRecTest.assert_char_array(len(exc_desc), exc_desc);

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = WRR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 2, 20)
#   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num);
#   Test SITE_GRP, position 4, value of site_grp variable
    stdfRecTest.assert_instance_field(inst, 4, site_grp);
#   Test FINISH_T, position 5, value of finish_t variable
    stdfRecTest.assert_instance_field(inst, 5, finish_t);
#   Test PART_CNT, position 6, value of part_cnt variable
    stdfRecTest.assert_instance_field(inst, 6, part_cnt);
#   Test RTST_CNT, position 7, value of rtst_cnt variable
    stdfRecTest.assert_instance_field(inst, 7, rtst_cnt);
#   Test ABRT_CNT, position 8, value of abrt_cnt variable
    stdfRecTest.assert_instance_field(inst, 8, abrt_cnt);
#   Test GOOD_CNT, position 9, value of good_cnt variable
    stdfRecTest.assert_instance_field(inst, 9, good_cnt);
#   Test FUNC_CNT, position 10, value of func_cnt variable
    stdfRecTest.assert_instance_field(inst, 10, func_cnt);
#   Test WAFER_ID, position 11, value of wafer_id variable
    stdfRecTest.assert_instance_field(inst, 11, wafer_id);
#   Test FABWF_ID, position 12, value of fabwf_id variable
    stdfRecTest.assert_instance_field(inst, 12, fabwf_id);
#   Test FRAME_ID, position 13, value of frame_id variable
    stdfRecTest.assert_instance_field(inst, 13, frame_id);
#   Test MASK_ID, position 14, value of mask_id variable
    stdfRecTest.assert_instance_field(inst, 14, mask_id);
#   Test USR_DESC, position 15, value of usr_desc variable
    stdfRecTest.assert_instance_field(inst, 15, usr_desc);
#   Test EXC_DESC, position 16, value of exc_desc variable
    stdfRecTest.assert_instance_field(inst, 16, exc_desc);

    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf

#   ToDo: Test JSON output

    os.remove(tf.name)