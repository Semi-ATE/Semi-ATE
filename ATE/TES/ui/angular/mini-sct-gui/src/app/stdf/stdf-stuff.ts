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
  STDF_VER: 'STDF_VER'
};

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
export type SiteHead = string;

export type StdfRecordLabelType = string;
export type StdfRecordValueType = string | number | boolean;
export type StdfRecordEntryType = [StdfRecordLabelType, StdfRecordValueType];
export interface StdfRecord {
  type: StdfRecordType;
  values: StdfRecordEntryType[];
}

export let getStdfRecordDescription = (record: StdfRecord): string => {
  return STDF_RECORD_TYPE_LONG_FORM[record.type] ?? '';
};

export let stdfGetValue = (record: StdfRecord, label: StdfRecordLabelType): StdfRecordValueType => {
  return record?.values?.filter(([k, v]) => k === label)?.[0]?.[1];
};

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
