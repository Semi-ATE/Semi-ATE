from Semi_ATE.STDF import (PTR, PRR, PIR, TSR, SBR, HBR, MRR, MIR, PCR, FAR, FTR, SDR)

ENDIAN = '<'


def generate_PTR_dict(test_num, head_num, site_num,
                      is_pass, param_flag, measurement,
                      test_txt, alarm_id, l_limit, u_limit,
                      fmt, exponent, unit, ls_limit, us_limit,
                      opt_flag=2):
    record = {'type': 'PTR'}
    ptr_record = generate_PTR(test_num, head_num, site_num,
                              is_pass, param_flag, measurement,
                              test_txt, alarm_id, l_limit, u_limit,
                              unit, fmt, exponent, ls_limit, us_limit,
                              opt_flag).to_dict()
    ptr_record['TEST_FLG'] = flag_array_to_int(ptr_record['TEST_FLG'], ENDIAN)
    ptr_record['PARM_FLG'] = flag_array_to_int(ptr_record['PARM_FLG'], ENDIAN)
    ptr_record['OPT_FLAG'] = flag_array_to_int(ptr_record['OPT_FLAG'], ENDIAN)
    record.update(ptr_record)
    return record


def generate_PTR(test_num, head_num, site_num,
                 is_pass, param_flag, measurement,
                 test_txt, alarm_id, l_limit, u_limit,
                 unit, fmt, exponent, ls_limit, us_limit,
                 opt_flag=2):
    rec = PTR('V4', ENDIAN)

    format = f'%7{fmt}' if '%7' not in fmt else fmt

    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('TEST_NUM', test_num)

    rec.set_value('TEST_FLG', 0b00000000 if is_pass else 0b00000001)
    rec.set_value('PARM_FLG', param_flag)
    rec.set_value('RESULT', measurement if measurement is not None else ls_limit)
    rec.set_value('TEST_TXT', test_txt)
    rec.set_value('ALARM_ID', alarm_id)

    rec.set_value('C_RESFMT', format)
    rec.set_value('C_LLMFMT', format)
    rec.set_value('C_HLMFMT', format)

    rec.set_value('LO_LIMIT', l_limit)
    rec.set_value('HI_LIMIT', u_limit)

    rec.set_value('LO_SPEC', ls_limit)
    rec.set_value('HI_SPEC', us_limit)

    rec.set_value('RES_SCAL', exponent)
    rec.set_value('LLM_SCAL', exponent)
    rec.set_value('HLM_SCAL', exponent)

    rec.set_value('UNITS', ' ' if '˽' == unit else unit)

    # TODO: workaround, need to explicitly set this or serialization raises exception
    rec.set_value('OPT_FLAG', opt_flag)  # bit set means ignore some field

    # PTR is special in STDF, because all fields AFTER OPT_FLAG of the first PTR in the STDF file for a test defines the default values to be used for all following PTRs of the test
    # possibly not fully implemented here
    return rec


def generate_PIR_dict(head_num, site_num):
    record = {'type': 'PIR'}
    record.update(generate_PIR(head_num, site_num).to_dict())
    return record


def generate_PIR(head_num, site_num):
    rec = PIR('V4', '<')
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)

    return rec


def generate_PRR(head_num, site_num, is_pass,
                 num_tests, hard_bin, soft_bin,
                 x_coord, y_coord, test_time,
                 part_id, part_txt, part_fix):
    rec = PRR('V4', ENDIAN)

    # 2020-07-31: Force sbin to 1 if it was
    # not set by the user.
    if soft_bin < 0:
        soft_bin = 1

    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('PART_FLG', 0b00000000 if is_pass else 0b00001000)
    rec.set_value('NUM_TEST', num_tests)
    rec.set_value('HARD_BIN', hard_bin)
    rec.set_value('SOFT_BIN', soft_bin)
    rec.set_value('X_COORD', x_coord)
    rec.set_value('Y_COORD', y_coord)
    rec.set_value('TEST_T', test_time)
    rec.set_value('PART_ID', part_id)
    rec.set_value('PART_TXT', part_txt)
    rec.set_value('PART_FIX', part_fix)
    return rec


def generate_PRR_dict(head_num, site_num, is_pass,
                      num_tests, hard_bin, soft_bin,
                      x_coord, y_coord, test_time,
                      part_id, part_txt, part_fix):
    record = {'type': 'PRR'}
    prr_record = generate_PRR(head_num, site_num, is_pass,
                              num_tests, hard_bin, soft_bin,
                              x_coord, y_coord, test_time,
                              part_id, part_txt, part_fix).to_dict()
    prr_record['PART_FLG'] = flag_array_to_int(prr_record['PART_FLG'], ENDIAN)
    prr_record['PART_FIX'] = flag_array_to_int(prr_record['PART_FIX'], ENDIAN)
    record.update(prr_record)
    return record


def generate_TSR(head_num, site_num, test_typ, test_num,
                 exec_cnt, fail_cnt, alarm_cnt, test_nam,
                 seq_name, test_lbl, opt_flag, test_tim,
                 test_min, test_max, tst_sums, tst_sqrs):
    rec = TSR('V4', ENDIAN)

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

    return rec


def generate_TSR_dict(head_num, site_num, test_typ, test_num,
                      exec_cnt, fail_cnt, alarm_cnt, test_nam,
                      seq_name, test_lbl, opt_flag, test_tim,
                      test_min, test_max, tst_sums, tst_sqrs):
    record = {'type': 'TSR'}
    tsr_record = generate_TSR(head_num, site_num, test_typ, test_num,
                              exec_cnt, fail_cnt, alarm_cnt, test_nam,
                              seq_name, test_lbl, opt_flag, test_tim,
                              test_min, test_max, tst_sums, tst_sqrs).to_dict()
    tsr_record['OPT_FLAG'] = flag_array_to_int(tsr_record['OPT_FLAG'], ENDIAN)
    record.update(tsr_record)
    return record


def flag_array_to_int(flags, endian):
    counter = 1
    if endian == '<':
        counter = -1

    if not flags:
        return

    num = 0
    for index, flag in enumerate(flags[::counter]):
        num += pow(2, index) * int(flag)

    return num


def generate_FTR(test_num, head_num, site_num, exception, opt_flag=255):
    rec = FTR('V4', endian=ENDIAN)
    rec.set_value('TEST_NUM', test_num)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('TEST_FLG', 0b10000000 if exception else 0b00000001)
    # RTN_ICNT and PGM_ICNT field must be initialized to satisfy the stdf-record generator
    rec.set_value('RTN_ICNT', 0)
    rec.set_value('PGM_ICNT', 0)
    rec.set_value('OPT_FLAG', opt_flag)
    return rec


def generate_FTR_dict(test_num, head_num, site_num, exception):
    record = {'type': 'FTR'}
    ftr_record = generate_FTR(test_num, head_num, site_num, exception).to_dict()
    ftr_record['TEST_FLG'] = flag_array_to_int(ftr_record['TEST_FLG'], ENDIAN)
    ftr_record['OPT_FLAG'] = flag_array_to_int(ftr_record['OPT_FLAG'], ENDIAN)
    record.update(ftr_record)
    return record


def generate_SBR(head_num: int, site_num: int, bin_num: int, count: int, bin_name: str, bin_pf: str) -> SBR:
    rec = SBR('V4', endian=ENDIAN)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('SBIN_NUM', bin_num)
    rec.set_value('SBIN_CNT', count)
    rec.set_value('SBIN_PF', bin_pf)
    rec.set_value('SBIN_NAM', bin_name)
    return rec


def generate_HBR(head_num: int, site_num: int, bin_num: int, count: int, bin_name: str, bin_pf: str) -> HBR:
    rec = HBR('V4', endian=ENDIAN)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)
    rec.set_value('HBIN_NUM', bin_num)
    rec.set_value('HBIN_CNT', count)
    rec.set_value('HBIN_PF', bin_pf)
    rec.set_value('HBIN_NAM', bin_name)
    return rec


def generate_MRR(end_timestamp: int) -> MRR:
    rec = MRR('V4', endian=ENDIAN)
    rec.set_value('FINISH_T', end_timestamp)
    return rec


def generate_MIR(setup_time: int, start_time: int, stat_num: int, lot_id: str,
                 part_typ: str, node_name: str, tstr_typ: str, job_name: str,
                 operator_name: str, test_temp: str, user_text: str,
                 package_type: str, sublot_id: str) -> MIR:
    rec = MIR('V4', endian=ENDIAN)

    rec.set_value('SETUP_T', setup_time)
    rec.set_value('START_T', start_time)
    rec.set_value('STAT_NUM', stat_num)
    rec.set_value('MODE_COD', 'P')  # TODO: maybe testprogram can provide this information
    rec.set_value('LOT_ID', lot_id)
    rec.set_value('PART_TYP', part_typ)
    rec.set_value('NODE_NAM', node_name)
    rec.set_value('TSTR_TYP', tstr_typ)
    rec.set_value('JOB_NAM', job_name)
    rec.set_value('SBLOT_ID', sublot_id)
    rec.set_value('OPER_NAM', operator_name)
    rec.set_value('EXEC_VER', job_name)
    rec.set_value('TST_TEMP', test_temp)
    rec.set_value('USER_TXT', user_text)
    rec.set_value('PKG_TYP', package_type)

    return rec


def generate_PCR(head_num: int, site_num: int, part_count: int, retest_count: int,
                 abort_count: int, good_count: int, functional_count: int) -> PCR:
    rec = PCR('V4', endian=ENDIAN)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_NUM', site_num)

    rec.set_value('PART_CNT', part_count)
    rec.set_value('RTST_CNT', retest_count)
    rec.set_value('ABRT_CNT', abort_count)
    rec.set_value('GOOD_CNT', good_count)
    rec.set_value('FUNC_CNT', functional_count)

    return rec


def generate_FAR(cpu_type: int, stdf_ver: int) -> FAR:
    rec = FAR('V4', endian=ENDIAN)
    rec.set_value('CPU_TYPE', cpu_type)
    rec.set_value('STDF_VER', stdf_ver)
    return rec


def generate_SDR(head_num: int, site_grp: int, site_cnt: int, site_nums: list) -> SDR:
    rec = SDR('V4', endian=ENDIAN)
    rec.set_value('HEAD_NUM', head_num)
    rec.set_value('SITE_GRP', site_grp)
    rec.set_value('SITE_CNT', site_cnt)
    rec.set_value('SITE_NUM', [int(site_num) for site_num in site_nums])
    return rec
