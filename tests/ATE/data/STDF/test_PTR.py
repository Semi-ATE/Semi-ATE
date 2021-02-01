import os
import tempfile
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF.PTR import PTR

#   Parametric Test Record
#   Function:
#   Contains the results of a single execution of a parametric test in the 
#   test program. Thefirst occurrence of this record also establishes the 
#   default values for all semi-staticinformation about the test, such as 
#   limits, units, and scaling. ThePTRis related to theTest Synopsis Record 
#   (TSR) by test number, head number, and site number
    
def test_PTR():
    
#   ATDF page 43
    expected_atdf = "PTR:"
#   record length in bytes    
    rec_len = 0;

#   STDF v4 page 47
    record = PTR()

    test_num = 123
    record.set_value('TEST_NUM', test_num)
    rec_len += 4;
    expected_atdf += str(test_num) +"|"

    head_num = 1 
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) +"|"

    site_num = 1
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"


#    The order of fields is different in STDF and ATDF for PTR record
#    
#    STDF page 47| ATDF page 43
#    
#    TEST_NUM    = TEST_NUM   
#    HEAD_NUM    = HEAD_NUM    
#    SITE_NUM    = SITE_NUM  
#    TEST_FLG    
#    PARM_FLG        
#    RESULT      = RESULT
#                  TEST_FLG bits 6 and 7
#                  PARM_FLG bit 5
#                  TEST_FLG bits 0, 2, 3, 4, 5
#                  PARM_FLG bits 0, 1, 2, 3, 4
#    TEST_TXT    = TEST_TXT 
#    ALARM_ID    = ALARM_ID  
#    OPT_FLAG    > missing        
#                  PARM_FLG bits 6 and 7
#    RES_SCAL
#    LLM_SCAL
#    HLM_SCAL
#    LO_LIMIT
#    HI_LIMIT
#    UNITS       = UNITS  
#                  LO_LIMIT
#                  HI_LIMIT
#    C_RESFMT    = C_RESFMT  
#    C_LLMFMT    = C_LLMFMT  
#    C_HLMFMT    = C_HLMFMT  
#    LO_SPEC     = LO_SPEC  
#    HI_SPEC     = HI_SPEC  
#                  RES_SCAL
#                  LLM_SCAL
#                  HLM_SCAL
#    

    test_flg = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('TEST_FLG', test_flg)
    rec_len += 1;

    parm_flg = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('PARM_FLG', parm_flg)
    rec_len += 1;

    result = 2.345
    record.set_value('RESULT', result)
    rec_len += 4;
    expected_atdf += str(result) + "|"

#    TEST_FLG bits 6 and 7
#    PARM_FLG bit 5
    expected_atdf += ' ' + "|"
#    TEST_FLG bits 0, 2, 3, 4, 5
#    PARM_FLG bits 0, 1, 2, 3, 4
    expected_atdf += 'AUTNXSDOHL' + "|"

    test_txt = 'IDDQ during pattern exection' 
    record.set_value('TEST_TXT', test_txt)
    rec_len += len(test_txt) + 1;
    expected_atdf += test_txt + "|"

    alarm_id = 'CRASH_ALARM_ID' 
    record.set_value('ALARM_ID', alarm_id)
    rec_len += len(alarm_id) + 1;
    expected_atdf += alarm_id + "|"

#    PARM_FLG bits 6 and 7
#    Not clear documentation what to expect here
    expected_atdf += 'LH' + "|"

    opt_flag = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('OPT_FLAG', opt_flag)
    rec_len += 1;

    res_scal = 10
    record.set_value('RES_SCAL', res_scal)
    rec_len += 1;

    llm_scal = 10
    record.set_value('LLM_SCAL', llm_scal)
    rec_len += 1;

    hlm_scal = 10
    record.set_value('HLM_SCAL', hlm_scal)
    rec_len += 1;

    lo_limit = 1.001
    record.set_value('LO_LIMIT', lo_limit)
    rec_len += 4;
    
    hi_limit = 1.999
    record.set_value('HI_LIMIT', hi_limit)
    rec_len += 4;

    units = 'mV'
    record.set_value('UNITS', units)
    rec_len += len(units) + 1;
    expected_atdf += str(units) + "|"

    expected_atdf += str(lo_limit) + "|"
    expected_atdf += str(hi_limit) + "|"

    c_resfmt = '%3.3f'
    record.set_value('C_RESFMT', c_resfmt)
    rec_len += len(c_resfmt) + 1;
    expected_atdf += str(c_resfmt) + "|"

    c_llmfmt = '%3.6f'
    record.set_value('C_LLMFMT', c_llmfmt)
    rec_len += len(c_llmfmt) + 1;
    expected_atdf += str(c_llmfmt) + "|"

    c_hlmfmt = '%3.6f'
    record.set_value('C_HLMFMT', c_hlmfmt)
    rec_len += len(c_hlmfmt) + 1;
    expected_atdf += str(c_hlmfmt) + "|"

    lo_spec = 1.001
    record.set_value('LO_SPEC', lo_spec)
    rec_len += 4;
    
    hi_spec = 1.999
    record.set_value('HI_SPEC', hi_spec)
    rec_len += 4;

    expected_atdf += str(lo_spec) + "|"
    expected_atdf += str(hi_spec) + "|"

    expected_atdf += str(res_scal) + "|"
    expected_atdf += str(llm_scal) + "|"
    expected_atdf += str(hlm_scal)


#    Test serialization
#    1. Save PTR STDF record into a file
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
    stdfRecTest.assert_file_record_header(rec_len, 15, 10)
#   Test TEST_NUM, expected value test_num
    stdfRecTest.assert_int(4, test_num)
#   Test HEAD_NUM, expected value head_num
    stdfRecTest.assert_int(1, head_num)
#   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int(1, site_num)
#   Test TEST_FLAG, expected value test_flg
    stdfRecTest.assert_bits(test_flg)
#   Test PARM_FLAG, expected value parm_flg
    stdfRecTest.assert_bits(parm_flg)
#   Test RESULT, expected value result
    stdfRecTest.assert_float(result)
#   Test TEST_TXT, expected value test_txt
    stdfRecTest.assert_ubyte(len(test_txt))
    stdfRecTest.assert_char_array(len(test_txt), test_txt)
#   Test ALARM_ID, expected value alarm_id
    stdfRecTest.assert_ubyte(len(alarm_id))
    stdfRecTest.assert_char_array(len(alarm_id), alarm_id)
#   Test OPT_FLAG, expected value opt_flag
    stdfRecTest.assert_bits(opt_flag)
#   Test RES_SCAL, expected value res_scal
    stdfRecTest.assert_int(1, res_scal)
#   Test LLM_SCAL, expected value llm_scal
    stdfRecTest.assert_int(1, llm_scal)
#   Test HLM_SCAL, expected value hlm_scal
    stdfRecTest.assert_int(1, hlm_scal)
#   Test LO_LIMIT, expected value lo_limit
    stdfRecTest.assert_float(lo_limit)
#   Test HI_LIMIT, expected value hi_limit
    stdfRecTest.assert_float(hi_limit)
#   Test UNITS, expected value units
    stdfRecTest.assert_ubyte(len(units))
    stdfRecTest.assert_char_array(len(units), units)
#   Test C_RESFMT, expected value c_resfmt
    stdfRecTest.assert_ubyte(len(c_resfmt))
    stdfRecTest.assert_char_array(len(c_resfmt), c_resfmt)
#   Test C_LLMFMT, expected value c_llmfmt
    stdfRecTest.assert_ubyte(len(c_llmfmt))
    stdfRecTest.assert_char_array(len(c_llmfmt), c_llmfmt)
#   Test C_HLMFMT, expected value c_hlmfmt
    stdfRecTest.assert_ubyte(len(c_hlmfmt))
    stdfRecTest.assert_char_array(len(c_hlmfmt), c_hlmfmt)
#   Test LO_SPEC, expected value lo_spec
    stdfRecTest.assert_float(lo_spec)
#   Test HI_SPEC, expected value hi_spec
    stdfRecTest.assert_float(hi_spec)


    
    f.close()    

#    Test de-serialization
#    1. Open STDF record from a file
#    2. Read record fields and compare with the expected value
#    
#    ToDo : make test with both endianness

    inst = PTR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 15, 10)
#   Test TEST_NUM, position 3, value of test_num variable
    stdfRecTest.assert_instance_field(inst, 3, test_num);
#   Test HEAD_NUM, position 4, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 4, head_num);
#   Test SITE_NUM, position 5, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 5, site_num);
#   Test TEST_FLG, position 6, value of test_flg variable
    stdfRecTest.assert_instance_field(inst, 6, test_flg);
#   Test PARM_FLG, position 7, value of parm_flg variable
    stdfRecTest.assert_instance_field(inst, 7, parm_flg);
#   Test RESULT, position 8, value of result variable
    stdfRecTest.assert_instance_field(inst, 8, result);
#   Test TEST_TXT, position 9, value of test_txt variable
    stdfRecTest.assert_instance_field(inst, 9, test_txt);
#   Test ALARM_ID, position 10, value of alarm_id variable
    stdfRecTest.assert_instance_field(inst, 10, alarm_id);
#   Test OPT_FLAG, position 11, value of opt_flag variable
    stdfRecTest.assert_instance_field(inst, 11, opt_flag);
#   Test RES_SCAL, position 12, value of res_scal variable
    stdfRecTest.assert_instance_field(inst, 12, res_scal);
#   Test LLM_SCAL, position 13, value of llm_scal variable
    stdfRecTest.assert_instance_field(inst, 13, llm_scal);
#   Test HLM_SCAL, position 14, value of hlm_scal variable
    stdfRecTest.assert_instance_field(inst, 14, hlm_scal);
#   Test LO_LIMIT, position 15, value of lo_limit variable
    stdfRecTest.assert_instance_field(inst, 15, lo_limit);
#   Test HI_LIMIT, position 16, value of hi_limit variable
    stdfRecTest.assert_instance_field(inst, 16, hi_limit);
#   Test UNITS, position 17, value of units variable
    stdfRecTest.assert_instance_field(inst, 17, units);
#   Test C_RESFMT, position 18, value of c_resfmt variable
    stdfRecTest.assert_instance_field(inst, 18, c_resfmt);
#   Test C_LLMFMT, position 19, value of c_llmfmt variable
    stdfRecTest.assert_instance_field(inst, 19, c_llmfmt);
#   Test C_HLMFMT, position 20, value of c_hlmfmt variable
    stdfRecTest.assert_instance_field(inst, 20, c_hlmfmt);
#   Test LO_SPEC, position 21, value of lo_spec variable
    stdfRecTest.assert_instance_field(inst, 21, lo_spec);
#   Test HI_SPEC, position 22, value of hi_spec variable
    stdfRecTest.assert_instance_field(inst, 22, hi_spec);
    
#   Test ATDF output
    assert inst.to_atdf() == expected_atdf
    
#   Test rest and OPT_FLAG    
    rec_len = 0;
    record.reset()

    test_num = 123
    record.set_value('TEST_NUM', test_num)
    rec_len += 4;
    expected_atdf += str(test_num) +"|"

    head_num = 1 
    record.set_value('HEAD_NUM', head_num)
    rec_len += 1;
    expected_atdf += str(head_num) +"|"

    site_num = 1
    record.set_value('SITE_NUM', site_num)
    rec_len += 1;
    expected_atdf += str(site_num) + "|"


    test_flg = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('TEST_FLG', test_flg)
    rec_len += 1;

    parm_flg = ['1', '1', '1', '1', '1', '1', '1', '1']
    record.set_value('PARM_FLG', parm_flg)
    rec_len += 1;

    result = 2.345
    record.set_value('RESULT', result)
    rec_len += 4;
    expected_atdf += str(result) + "|"

#    TEST_FLG bits 6 and 7
#    PARM_FLG bit 5
    expected_atdf += ' ' + "|"
#    TEST_FLG bits 0, 2, 3, 4, 5
#    PARM_FLG bits 0, 1, 2, 3, 4
    expected_atdf += 'AUTNXSDOHL' + "|"

    test_txt = 'IDDQ during pattern exection' 
    record.set_value('TEST_TXT', test_txt)
    rec_len += len(test_txt) + 1;
    expected_atdf += test_txt + "|"

    alarm_id = 'CRASH_ALARM_ID' 
    record.set_value('ALARM_ID', alarm_id)
    rec_len += len(alarm_id) + 1;
    expected_atdf += alarm_id + "|"

    f = open(tf.name, "wb")
    w_data = record.__repr__()
    f.write(w_data)
    f.close

    f = open(tf.name, "rb")
    
    stdfRecTest = STDFRecordTest(f, "<")

    inst = PTR('V4', '<', w_data)
#   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst , rec_len, 15, 10)

#   ToDo: Test JSON output
    
    os.remove(tf.name)
