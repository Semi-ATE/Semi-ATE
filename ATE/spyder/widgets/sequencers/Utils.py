from ATE.data.STDF.records import (PTR, PRR, PIR, TSR)


def generate_PTR(test_num, head_num, site_num,
                 is_pass, param_flag, measurement,
                 test_txt, alarm_id, opt_flag=255):
    rec = PTR('V4', '<')

    rec.set_value('TEST_NUM', test_num)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)

    rec.set_value('TEST_FLG', 0b01000000 if is_pass else 0b01000001)  # bit 1 set === 'RESULT' is valid, bit 7 set = test failed
    rec.set_value('PARM_FLG', param_flag)
    rec.set_value('RESULT', measurement)
    rec.set_value('TEST_TXT', test_txt)
    rec.set_value('ALARM_ID', alarm_id)

    # TODO: workaround, need to explicitly set this or serialization raises exception
    rec.set_value('OPT_FLAG', opt_flag)  # bit set means ignore some field

    # PTR is special in STDF, because all fields AFTER OPT_FLAG of the first PTR in the STDF file for a test defines the default values to be used for all following PTRs of the test
    # possibly not fully implemented here
    record = {'type': 'PTR'}
    record.update(rec.to_dict())
    return record


def generate_PIR(head_num, site_num):
    rec = PIR('V4', '<')
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)

    record = {'type': 'PIR'}
    record.update(rec.to_dict())
    return record


def generate_PRR(head_num, site_num, part_flag,
                 num_tests, hard_bin, soft_bin,
                 x_coord, y_coord, test_time,
                 part_id, part_txt, part_fix):
    rec = PRR('V4', '<')

    # 2020-07-31: Force sbin to 1 if it was
    # not set by the user.
    if soft_bin < 0:
        soft_bin = 1

    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('PART_FLG', part_flag)
    rec.set_value('NUM_TEST', num_tests)
    rec.set_value('HARD_BIN', hard_bin)
    rec.set_value('SOFT_BIN', soft_bin)
    rec.set_value('X_COORD', x_coord)
    rec.set_value('Y_COORD', y_coord)
    rec.set_value('TEST_T', test_time)
    rec.set_value('PART_ID', part_id)
    rec.set_value('PART_TXT', part_txt)
    rec.set_value('PART_FIX', part_fix)

    record = {'type': 'PRR'}
    record.update(rec.to_dict())
    return record

def generate_TSR(head_num, site_num, test_typ, test_num,
                 exec_cnt, fail_cnt, alarm_cnt, test_nam,
                 seq_name, test_lbl, opt_flag, test_tim,
                 test_min, test_max, tst_sums, tst_sqrs):
    rec = TSR('V4', '<')

    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('TEST_TYP', test_typ)
    rec.set_value('TEST_NUM', test_num)
    rec.set_value('EXEC_CNT', exec_cnt)
    rec.set_value('FAIL_CNT', fail_cnt)
    rec.set_value('ALRM_CNT', alarm_cnt)
    rec.set_value('TEST_NAM', test_nam)
    rec.set_value('SEQ_NAME', seq_name)
    rec.set_value('TEST_LBL', test_lbl)
    rec.set_value('OPT_FLAG', opt_flag)
    rec.set_value('TEST_TIM', test_tim)
    rec.set_value('TEST_MIN', test_min)
    rec.set_value('TEST_MAX', test_max)
    rec.set_value('TST_SUMS', tst_sums)
    rec.set_value('TST_SQRS', tst_sqrs)

    record = {'type': 'TSR'}
    record.update(rec.to_dict())
    return record
