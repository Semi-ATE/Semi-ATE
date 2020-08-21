# this is a small programm that returns the unique data types from the stdf standard V4 in alphabetic order.
# I am lazy and just copied them from the pystdf package and then double checked and renamed according to the documentation.


FAR = (("CPU_TYPE", "U1"), ("STDF_VER", "U1"))

ATR = (("MOD_TIM", "U4"), ("CMD_LINE", "Cn"))

MIR = (
    ("SETUP_T", "U4"),
    ("START_T", "U4"),
    ("STAT_NUM", "U1"),
    ("MODE_COD", "C1"),
    ("RTST_COD", "C1"),
    ("PROT_COD", "C1"),
    ("BURN_TIM", "U2"),
    ("CMOD_COD", "C1"),
    ("LOT_ID", "Cn"),
    ("PART_TYP", "Cn"),
    ("NODE_NAM", "Cn"),
    ("TSTR_TYP", "Cn"),
    ("JOB_NAM", "Cn"),
    ("JOB_REV", "Cn"),
    ("SBLOT_ID", "Cn"),
    ("OPER_NAM", "Cn"),
    ("EXEC_TYP", "Cn"),
    ("EXEC_VER", "Cn"),
    ("TEST_COD", "Cn"),
    ("TST_TEMP", "Cn"),
    ("USER_TXT", "Cn"),
    ("AUX_FILE", "Cn"),
    ("PKG_TYP", "Cn"),
    ("FAMLY_ID", "Cn"),
    ("DATE_COD", "Cn"),
    ("FACIL_ID", "Cn"),
    ("FLOOR_ID", "Cn"),
    ("PROC_ID", "Cn"),
    ("OPER_FRQ", "Cn"),
    ("SPEC_NAM", "Cn"),
    ("SPEC_VER", "Cn"),
    ("FLOW_ID", "Cn"),
    ("SETUP_ID", "Cn"),
    ("DSGN_REV", "Cn"),
    ("ENG_ID", "Cn"),
    ("ROM_COD", "Cn"),
    ("SERL_NUM", "Cn"),
    ("SUPR_NAM", "Cn"),
)

MRR = (("FINISH_T", "U4"), ("DISP_COD", "C1"), ("USR_DESC", "Cn"), ("EXC_DESC", "Cn"))

PCR = (
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("PART_CNT", "U4"),
    ("RTST_CNT", "U4"),
    ("ABRT_CNT", "U4"),
    ("GOOD_CNT", "U4"),
    ("FUNC_CNT", "U4"),
)

HBR = (
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("HBIN_NUM", "U2"),
    ("HBIN_CNT", "U4"),
    ("HBIN_PF", "C1"),
    ("HBIN_NAM", "Cn"),
)

SBR = (
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("SBIN_NUM", "U2"),
    ("SBIN_CNT", "U4"),
    ("SBIN_PF", "C1"),
    ("SBIN_NAM", "Cn"),
)

PMR = (
    ("PMR_INDX", "U2"),
    ("CHAN_TYP", "U2"),
    ("CHAN_NAM", "Cn"),
    ("PHY_NAM", "Cn"),
    ("LOG_NAM", "Cn"),
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
)

PGR = (("GRP_INDX", "U2"), ("GRP_NAM", "Cn"), ("INDX_CNT", "U2"), ("PMR_INDX", "kxU2"))

PLR = (
    ("GRP_CNT", "U2"),
    ("GRP_INDX", "kxU2"),
    ("GRP_MODE", "kxU2"),
    ("GRP_RADX", "kxU1"),
    ("PGM_CHAR", "kxCn"),
    ("RTN_CHAR", "kxCn"),
    ("PGM_CHAL", "kxCn"),
    ("RTN_CHAL", "kxCn"),
)

RDR = (("NUM_BINS", "U2"), ("RTST_BIN", "kxU2"))

SDR = (
    ("HEAD_NUM", "U1"),
    ("SITE_GRP", "U1"),
    ("SITE_CNT", "U1"),
    ("SITE_NUM", "kxU1"),
    ("HAND_TYP", "Cn"),
    ("HAND_ID", "Cn"),
    ("CARD_TYP", "Cn"),
    ("CARD_ID", "Cn"),
    ("LOAD_TYP", "Cn"),
    ("LOAD_ID", "Cn"),
    ("DIB_TYP", "Cn"),
    ("DIB_ID", "Cn"),
    ("CABL_TYP", "Cn"),
    ("CABL_ID", "Cn"),
    ("CONT_TYP", "Cn"),
    ("CONT_ID", "Cn"),
    ("LASR_TYP", "Cn"),
    ("LASR_ID", "Cn"),
    ("EXTR_TYP", "Cn"),
    ("EXTR_ID", "Cn"),
)

WIR = (("HEAD_NUM", "U1"), ("SITE_GRP", "U1"), ("START_T", "U4"), ("WAFER_ID", "Cn"))

WRR = (
    ("HEAD_NUM", "U1"),
    ("SITE_GRP", "U1"),
    ("FINISH_T", "U4"),
    ("PART_CNT", "U4"),
    ("RTST_CNT", "U4"),
    ("ABRT_CNT", "U4"),
    ("GOOD_CNT", "U4"),
    ("FUNC_CNT", "U4"),
    ("WAFER_ID", "Cn"),
    ("FABWF_ID", "Cn"),
    ("FRAME_ID", "Cn"),
    ("MASK_ID", "Cn"),
    ("USR_DESC", "Cn"),
    ("EXC_DESC", "Cn"),
)

WCR = (
    ("WAFR_SIZ", "R4"),
    ("DIE_HT", "R4"),
    ("DIE_WID", "R4"),
    ("WF_UNITS", "U1"),
    ("WF_FLAT", "C1"),
    ("CENTER_X", "I2"),
    ("CENTER_Y", "I2"),
    ("POS_X", "C1"),
    ("POS_Y", "C1"),
)

PIR = (("HEAD_NUM", "U1"), ("SITE_NUM", "U1"))

PRR = (
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("PART_FLG", "B1"),
    ("NUM_TEST", "U2"),
    ("HARD_BIN", "U2"),
    ("SOFT_BIN", "U2"),
    ("X_COORD", "I2"),
    ("Y_COORD", "I2"),
    ("TEST_T", "U4"),
    ("PART_ID", "Cn"),
    ("PART_TXT", "Cn"),
    ("PART_FIX", "Bn"),
)

TSR = (
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("TEST_TYP", "C1"),
    ("TEST_NUM", "U4"),
    ("EXEC_CNT", "U4"),
    ("FAIL_CNT", "U4"),
    ("ALRM_CNT", "U4"),
    ("TEST_NAM", "Cn"),
    ("SEQ_NAME", "Cn"),
    ("TEST_LBL", "Cn"),
    ("OPT_FLAG", "B1"),
    ("TEST_TIM", "R4"),
    ("TEST_MIN", "R4"),
    ("TEST_MAX", "R4"),
    ("TST_SUMS", "R4"),
    ("TST_SQRS", "R4"),
)

PTR = (
    ("TEST_NUM", "U4"),
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("TEST_FLG", "B1"),
    ("PARM_FLG", "B1"),
    ("RESULT", "R4"),
    ("TEST_TXT", "Cn"),
    ("ALARM_ID", "Cn"),
    ("OPT_FLAG", "B1"),
    ("RES_SCAL", "I1"),
    ("LLM_SCAL", "I1"),
    ("HLM_SCAL", "I1"),
    ("LO_LIMIT", "R4"),
    ("HI_LIMIT", "R4"),
    ("UNITS", "Cn"),
    ("C_RESFMT", "Cn"),
    ("C_LLMFMT", "Cn"),
    ("C_HLMFMT", "Cn"),
    ("LO_SPEC", "R4"),
    ("HI_SPEC", "R4"),
)

MPR = (
    ("TEST_NUM", "U4"),
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("TEST_FLG", "B1"),
    ("PARM_FLG", "B1"),
    ("RTN_ICNT", "U2"),
    ("RSLT_CNT", "U2"),
    ("RTN_STAT", "jxN1"),
    ("RTN_RSLT", "kxR4"),
    ("TEST_TXT", "Cn"),
    ("ALARM_ID", "Cn"),
    ("OPT_FLAG", "B1"),
    ("RES_SCAL", "I1"),
    ("LLM_SCAL", "I1"),
    ("HLM_SCAL", "I1"),
    ("LO_LIMIT", "R4"),
    ("HI_LIMIT", "R4"),
    ("START_IN", "R4"),
    ("INCR_IN", "R4"),
    ("RTN_INDX", "jxU2"),
    ("UNITS", "Cn"),
    ("UNITS_IN", "Cn"),
    ("C_RESFMT", "Cn"),
    ("C_LLMFMT", "Cn"),
    ("C_HLMFMT", "Cn"),
    ("LO_SPEC", "R4"),
    ("HI_SPEC", "R4"),
)

FTR = (
    ("TEST_NUM", "U4"),
    ("HEAD_NUM", "U1"),
    ("SITE_NUM", "U1"),
    ("TEST_FLG", "B1"),
    ("OPT_FLAG", "B1"),
    ("CYCL_CNT", "U4"),
    ("REL_VADR", "U4"),
    ("REPT_CNT", "U4"),
    ("NUM_FAIL", "U4"),
    ("XFAIL_AD", "I4"),
    ("YFAIL_AD", "I4"),
    ("VECT_OFF", "I2"),
    ("RTN_ICNT", "U2"),
    ("PGM_ICNT", "U2"),
    ("RTN_INDX", "jxU2"),
    ("RTN_STAT", "jxN1"),
    ("PGM_INDX", "kxU2"),
    ("PGM_STAT", "kxN1"),
    ("FAIL_PIN", "Dn"),
    ("VECT_NAM", "Cn"),
    ("TIME_SET", "Cn"),
    ("OP_CODE", "Cn"),
    ("TEST_TXT", "Cn"),
    ("ALARM_ID", "Cn"),
    ("PROG_TXT", "Cn"),
    ("RSLT_TXT", "Cn"),
    ("PATG_NUM", "U1"),
    ("SPIN_MAP", "Dn"),
)

BPS = (("SEQ_NAME", "Cn"),)

EPS = ()

GDR = (("GEN_DATA", "Vn"),)

DTR = (("TEXT_DAT", "Cn"),)

RecordTypes = {
    # Information about the STDF file
    "FAR": FAR,
    "ATR": ATR,
    # Data collected on a per lot basis
    "MIR": MIR,
    "MRR": MRR,
    "PCR": PCR,
    "HBR": HBR,
    "SBR": SBR,
    "PMR": PMR,
    "PGR": PGR,
    "PLR": PLR,
    "RDR": RDR,
    "SDR": SDR,
    # Data collected per wafer
    "WIR": WIR,
    "WRR": WRR,
    "WCR": WCR,
    # Data collected on a per part basis
    "PIR": PIR,
    "PRR": PRR,
    # Data collected per test in the test program
    "TSR": TSR,
    # Data collected per test execution
    "PTR": PTR,
    "MPR": MPR,
    "FTR": FTR,
    # Data collected per program segment
    "BPS": BPS,
    "EPS": EPS,
    # Generic Data
    "GDR": GDR,
    "DTR": DTR,
}


list_of_datatypes = []
for tup in RecordTypes.values():
    datatypes = [el[1] for el in tup]
    list_of_datatypes.append(datatypes)

list_of_datatypes_flat = [val for sublist in list_of_datatypes for val in sublist]

list_of_unique_datatypes_flat = list(set(list_of_datatypes_flat))
list_of_unique_datatypes_flat.sort()

print(list_of_unique_datatypes_flat)

