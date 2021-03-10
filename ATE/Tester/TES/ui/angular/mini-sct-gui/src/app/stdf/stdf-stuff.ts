import { sprintf } from 'sprintf-js';

export enum StdfRecordType {
  Unknown = '',
  Far = 'FAR',
  Atr = 'ATR',
  Mir = 'MIR',
  Mrr = 'MRR',
  Pcr = 'PCR',
  Hbr = 'HBR',
  Sbr = 'SBR',
  Pmr = 'PMR',
  Pgr = 'PGR',
  Plr = 'PLR',
  Rdr = 'RDR',
  Sdr = 'SDR',
  Wir = 'WIR',
  Wrr = 'WRR',
  Wcr = 'WCR',
  Pir = 'PIR',
  Prr = 'PRR',
  Tsr = 'TSR',
  Ptr = 'PTR',
  Mpr = 'MPR',
  Ftr = 'FTR',
  Bps = 'BPS',
  Eps = 'EPS',
  Gdr = 'GDR',
  Dtr = 'DTR',
}

export const STDF_RECORD_TYPE_LONG_FORM = {
  FAR: 'File Attributes',
  ATR: 'Audit Trail',
  MIR: 'Master Information',
  MRR: 'Master Results',
  PCR: 'Part Count',
  HBR: 'Hardware Bin',
  SBR: 'Software Bin',
  PMR: 'Pin Map',
  PGR: 'Pin Group',
  PLR: 'Pin List',
  RDR: 'Retest Data',
  SDR: 'Site Description',
  WIR: 'Wafer Information',
  WRR: 'Wafer Results',
  WCR: 'Wafer Configuration',
  PIR: 'Part Information',
  PRR: 'Part Results',
  TSR: 'Test Synopsis',
  PTR: 'Parametric Test',
  MPR: 'Multiple-Result Parametric',
  FTR: 'Functional Test',
  BPS: 'Begin Program Section',
  EPS: 'End Program Section',
  GDR: 'Generic Data',
  DTR: 'Datalog Text',
};

export enum MirTanslationMap {
  SETUP_T  = 'Date and time of job setup',
  START_T  = 'Date and time first part tested',
  STAT_NUM = 'Tester station number',
  MODE_COD = 'Test mode code (e.g. prod, dev) space',
  RTST_COD = 'Lot retest code space',
  PROT_COD = 'Data protection code space',
  BURN_TIM = 'Burn-in time (in minutes) 65,535',
  CMOD_COD = 'Command mode code space',
  LOT_ID   = 'Lot ID (customer specified)',
  PART_TYP = 'Part Type (or product ID)',
  NODE_NAM = 'Name of node that generated data',
  TSTR_TYP = 'Tester type',
  JOB_NAM  = 'Job name (test program name)',
  JOB_REV  = 'Job (test program) revision number length byte = 0',
  SBLOT_ID = 'Sublot ID length byte = 0',
  OPER_NAM = 'Operator name or ID (at setup time) length byte = 0',
  EXEC_TYP = 'Tester executive software type length byte = 0',
  EXEC_VER = 'Tester exec software version number length byte = 0',
  TEST_COD = 'Test phase or step code length byte = 0',
  TST_TEMP = 'Test temperature length byte = 0',
  USER_TXT = 'Generic user text length byte = 0',
  AUX_FILE = 'Name of auxiliary data file length byte = 0',
  PKG_TYP  = 'Package type length byte = 0',
  FAMLY_ID = 'Product family ID length byte = 0',
  DATE_COD = 'Date code length byte = 0',
  FACIL_ID = 'Test facility ID length byte = 0',
  FLOOR_ID = 'Test floor ID length byte = 0',
  PROC_ID  = 'Fabrication process ID length byte = 0',
  OPER_FRQ = 'Operation frequency or step length byte = 0',
  SPEC_NAM = 'Test specification name length byte = 0',
  SPEC_VER = 'Test specification version number length byte = 0',
  FLOW_ID  = 'Test flow ID length byte = 0',
  SETUP_ID = 'Test setup ID length byte = 0',
  DSGN_REV = 'Device design revision length byte = 0',
  ENG_ID   = 'Engineering lot ID length byte = 0',
  ROM_COD  = 'ROM code ID length byte = 0',
  SERL_NUM = 'Tester serial number length byte = 0',
  SUPR_NAM = 'Supervisor name or ID length byte = 0'
}

export enum MatchCodeTranslation {
  // MODE_COD
  A = 'AEL (Automatic Edge Lock) mode',
  C = 'Checker mode',
  D = 'Development / Debug test mode',
  E = 'Engineering mode (same as Development mode)',
  M = 'Maintenance mode',
  P = 'Production test mode',
  Q = 'Quality Control',
  // RTST_CODE
  Y = 'Lot was previously tested',
  N = 'Lot has not been previously tested',
  space = 'Not known if lot has been previously tested',
  number = 'Number of times lot has previously been tested'  // number = 0-9
}

export const STDF_RECORD_ATTRIBUTES = {
  SITE_NUM: 'SITE_NUM',
  HEAD_NUM: 'HEAD_NUM',
  PART_FLG: 'PART_FLG',
  NUM_TEST: 'NUM_TEST',
  HARD_BIN: 'HARD_BIN',
  SOFT_BIN: 'SOFT_BIN',
  X_COORD: 'X_COORD',
  Y_COORD: 'Y_COORD',
  TEST_T: 'TEST_T',
  PART_ID: 'PART_ID',
  PART_TXT: 'PART_TXT',
  PART_FIX: 'PART_FIX',
  CPU_TYPE: 'CPU_TYPE',
  STDF_VER: 'STDF_VER',
  TEST_FLG: 'TEST_FLG',
  TEST_TXT: 'TEST_TXT',
  TEST_NUM: 'TEST_NUM',
  RESULT: 'RESULT',
  UNITS: 'UNITS',
  C_RESLIMIT: 'C_RESLIMIT',
  RES_SCAL: 'RES_SCAL',
  LLM_SCAL: 'LLM_SCAL',
  HLM_SCAL: 'HLM_SCAL',
  LO_LIMIT: 'LO_LIMIT',
  HI_LIMIT: 'HI_LIMIT',
  C_RESFMT: 'C_RESFMT',
  C_LLMFMT: 'C_LLMFMT',
  C_HLMFMT: 'C_HLMFMT'
};

export const STDF_MIR_ATTRIBUTES = {
  SETUP_T: 'SETUP_T',
  START_T: 'START_T',
  STAT_NUM: 'STAT_NUM',
  MODE_COD: 'MODE_COD',
  RTST_COD: 'RTST_COD',
  PROT_COD: 'PROT_COD',
  BURN_TIM: 'BURN_TIM',
  CMOD_COD: 'CMOD_COD',
  LOT_ID: 'LOT_ID',
  PART_TYP: 'PART_TYP',
  NODE_NAM: 'NODE_NAM',
  TSTR_TYP: 'TSTR_TYP',
  JOB_NAM: 'JOB_NAM',
  JOB_REV: 'JOB_REV',
  SBLOT_ID: 'SBLOT_ID',
  OPER_NAM: 'OPER_NAM',
  EXEC_TYP: 'EXEC_TYP',
  EXEC_VER: 'EXEC_VER',
  TEST_COD: 'TEST_COD',
  TST_TEMP: 'TST_TEMP',
  USER_TXT: 'USER_TXT',
  AUX_FILE: 'AUX_FILE',
  PKG_TYP: 'PKG_TYP',
  FAMLY_ID: 'FAMLY_ID',
  DATE_COD: 'DATE_COD',
  FACIL_ID: 'FACIL_ID',
  FLOOR_ID: 'FLOOR_ID',
  PROC_ID: 'PROC_ID',
  OPER_FRQ: 'OPER_FRQ',
  SPEC_NAM: 'SPEC_NAM',
  SPEC_VER: 'SPEC_VER',
  FLOW_ID: 'FLOW_ID',
  SETUP_ID: 'SETUP_ID',
  DSGN_REV: 'DSGN_REV',
  ENG_ID: 'ENG_ID',
  ROM_COD: 'ROM_COD',
  SERL_NUM: 'SERL_NUM',
  SUPR_NAM: 'SUPR_NAM'
};

export enum MirAttributeDescriptionMap {
  SETUP_T = 'Setup Time',
  START_T = 'Start Time',
  STAT_NUM = 'Station Number',
  MODE_COD = 'Mode Code',
  RTST_COD = 'Retest Code',
  PROT_COD = 'Protection Code',
  BURN_TIM = 'Burn-in time',
  CMOD_COD = 'Cmod Code',
  LOT_ID = 'Lot ID',
  PART_TYP = 'Part Type',
  NODE_NAM = 'Node Name',
  TSTR_TYP = 'Tester Type',
  JOB_NAM = 'Job name',
  JOB_REV = 'Job Revision',
  SBLOT_ID = 'Sublot ID',
  OPER_NAM = 'Operator name',
  EXEC_TYP = 'Exec Type',
  EXEC_VER = 'Exec Version',
  TEST_COD = 'Test Code',
  TST_TEMP = 'Test Temperature',
  USER_TXT = 'User Text',
  AUX_FILE = 'Aux. File',
  PKG_TYP = 'Package type',
  FAMLY_ID = 'Family ID',
  DATE_COD = 'Date Code',
  FACIL_ID = 'Facility ID',
  FLOOR_ID = 'Floor ID',
  PROC_ID = 'Process ID',
  OPER_FRQ = 'Operation Frq.',
  SPEC_NAM = 'Spec. Name',
  SPEC_VER = 'Spec. Version',
  FLOW_ID = 'Flow ID',
  SETUP_ID = 'Setup Id',
  DSGN_REV = 'Design Revision',
  ENG_ID = 'Engineering Lot ID',
  ROM_COD = 'ROM Code',
  SERL_NUM = 'Serial Number',
  SUPR_NAM = 'Supervisor Name'
}

export const ALL_STDF_RECORD_TYPES = [
  StdfRecordType.Far,
  StdfRecordType.Atr,
  StdfRecordType.Mir,
  StdfRecordType.Mrr,
  StdfRecordType.Pcr,
  StdfRecordType.Hbr,
  StdfRecordType.Sbr,
  StdfRecordType.Pmr,
  StdfRecordType.Pgr,
  StdfRecordType.Plr,
  StdfRecordType.Rdr,
  StdfRecordType.Sdr,
  StdfRecordType.Wir,
  StdfRecordType.Wrr,
  StdfRecordType.Wcr,
  StdfRecordType.Pir,
  StdfRecordType.Prr,
  StdfRecordType.Tsr,
  StdfRecordType.Ptr,
  StdfRecordType.Mpr,
  StdfRecordType.Ftr,
  StdfRecordType.Bps,
  StdfRecordType.Eps,
  StdfRecordType.Gdr,
  StdfRecordType.Dtr,
];

export const STDF_RESULT_RECORDS = [StdfRecordType.Ptr, StdfRecordType.Mpr, StdfRecordType.Ftr];
export type SiteHead = string;

export type StdfRecordPropertyKey = string;
export type StdfRecordPropertyValue = string | number | boolean;
export interface StdfRecordProperty {
  key: StdfRecordPropertyKey;
  value: StdfRecordPropertyValue;
}
export interface StdfRecord {
  type: StdfRecordType;
  values: StdfRecordProperty[];
}

export class PrrRecord implements StdfRecord {
  readonly type: StdfRecordType = StdfRecordType.Prr;
  values: StdfRecordProperty[];
}

export class MirRecord implements StdfRecord {
  readonly type: StdfRecordType = StdfRecordType.Mir;
  values: StdfRecordProperty[];
  constructor() {
    this.values = [];
  }
}

export let getStdfRecordDescription = (record: StdfRecord): string => {
  return STDF_RECORD_TYPE_LONG_FORM[record.type] ?? '';
};

export let stdfGetValue = (record: StdfRecord, key: StdfRecordPropertyKey): StdfRecordPropertyValue =>
  record.values.find( e => e.key === key)?.value;


export let computeSiteHeadFromRecord = (record: StdfRecord): SiteHead => {
  let siteNumber = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.SITE_NUM) as number;
  let headNumber = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.HEAD_NUM) as number;
  return computeSiteHeadFromNumbers(siteNumber, headNumber);
};

export let computeSiteHeadFromNumbers = (site: number, head: number): SiteHead => {
  return site + '_' + head;
};

export let computePassedInformationForPartFlag = (partFlg: number): boolean => {
  let pass: boolean = ((partFlg & 4) === 0) && ((partFlg & 8) === 0) && ((partFlg & 16) === 0);
  return pass;
};

export let computePassedInformationForTestFlag = (testFlg: number): boolean => testFlg === 0;

export class Stdf {
  static readonly UNITS_PREFIX = {
    Femto: 'f',
    Pico: 'p',
    Nano: 'n',
    Micro: 'u',
    Milli: 'm',
    Percent: '%',
    Kilo: 'K',
    Mega: 'M',
    Giga: 'G',
    Tera: 'T',
  };

  static computeScaledUnits(scaleValue: number): string {
    switch(scaleValue) {
      case 15:
        return this.UNITS_PREFIX.Femto;
      case 12:
        return this.UNITS_PREFIX.Pico;
      case 9:
        return this.UNITS_PREFIX.Nano;
      case 6:
        return this.UNITS_PREFIX.Micro;
      case 3:
        return this.UNITS_PREFIX.Milli;
      case 2:
        return this.UNITS_PREFIX.Percent;
      case 0:
        return '';
      case -3:
        return this.UNITS_PREFIX.Kilo;
      case -6:
        return this.UNITS_PREFIX.Mega;
      case -9:
        return this.UNITS_PREFIX.Giga;
      case -12:
        return this.UNITS_PREFIX.Tera;
      default:
        return '';
    }
  }

  static computeScaledSTDFValues(value: number, scaling: number): number {
    let scaledValue = value * Math.pow(10, scaling);
    return scaledValue;
  }

  static computeUnits(record: StdfRecord): string {
    let units = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.UNITS) as string;
    return units;
  }

  static computeFormatString(record: StdfRecord, recordFormat: string): string {
    let format = stdfGetValue(record, recordFormat) as string;
    return format;
  }

  static getValue(fieldValueStr: string, scalingStr: string, format: string, record: StdfRecord): string {
    let fieldValue = stdfGetValue(record, fieldValueStr) as number;
    let scaling = stdfGetValue(record, scalingStr) as number;

    if(isNaN(fieldValue) || !isFinite(fieldValue)) {
      return fieldValue.toString();
    } else {
      return sprintf(this.computeFormatString(record, format), this.computeScaledSTDFValues(fieldValue, scaling)) + ' ' + this.computeScaledUnits(scaling) + this.computeUnits(record);
    }
  }

  static computeScaledResultFromSTDF(record: StdfRecord): string {
    return this.getValue(STDF_RECORD_ATTRIBUTES.RESULT, STDF_RECORD_ATTRIBUTES.RES_SCAL, STDF_RECORD_ATTRIBUTES.C_RESFMT, record);
  }

  static computeScaledLowLimitFromSTDF(record: StdfRecord): string {
    return this.getValue(STDF_RECORD_ATTRIBUTES.LO_LIMIT, STDF_RECORD_ATTRIBUTES.LLM_SCAL, STDF_RECORD_ATTRIBUTES.C_LLMFMT, record);
  }

  static computeScaledHighLimitFromSTDF(record: StdfRecord): string {
    return this.getValue(STDF_RECORD_ATTRIBUTES.HI_LIMIT, STDF_RECORD_ATTRIBUTES.HLM_SCAL, STDF_RECORD_ATTRIBUTES.C_HLMFMT, record);
  }
}

export const getSiteName = (siteNumber: number): string => {
  switch(siteNumber) {
    case 0:
      return 'A';
    case 1:
      return 'B';
    case 2:
      return 'C';
    case 3:
      return 'D';
    case 4:
      return 'E';
    case 5:
      return 'F';
    case 6:
      return 'G';
    case 7:
      return 'H';
    case 8:
      return 'I';
    case 9:
      return 'J';
    case 10:
      return 'K';
    case 11:
      return 'L';
    case 12:
      return 'M';
    case 13:
      return 'N';
    case 14:
      return 'O';
    case 15:
      return 'P';
    default:
      return 'unknown';
  }
};
