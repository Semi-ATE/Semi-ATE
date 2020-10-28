import { StdfRecord } from 'src/app/stdf/stdf-stuff';

export type ProgramFilterFunction = (e: StdfRecord[]) => boolean;
export type FilterFunction = (e: StdfRecord) => boolean;

export enum FilterType {
  RecordType = 0,
  SiteNumber = 1,
  TestNumber = 2,
  PassFail = 3,
  TestText = 4,
}

export interface SdtfRecordProgramFilter {
  filterFunction: ProgramFilterFunction;
  active: boolean;
}

export interface SdtfRecordFilter {
  filterFunction: FilterFunction;
  active: boolean;
  strengthen: boolean;
  readonly type: FilterType;
}
