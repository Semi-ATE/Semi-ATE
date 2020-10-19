import { StdfRecordType, ALL_STDF_RECORD_TYPES } from '../stdf/stdf-stuff';

export interface RecordTypeFilterSetting {
  selectedTypes: Array<StdfRecordType>;
}

export interface RecordViewAutoscrollSetting {
  enabled: boolean;
}

export interface SiteNumberFilterSetting {
  enabled: boolean;
  selectedSites: string;
}

export interface TestNumberFilterSetting {
  enabled: boolean;
  selectedTestNumbers: string;
}

export interface TestTextFilterSetting {
  enabled: boolean;
  containedTestText: string;
}

export interface PassFailFilterSetting {
  enabled: boolean;
  selectedIndex: number;
}

export interface ProgramFilterSetting {
  enabled: boolean;
  value: string;
}

export interface YieldSetting {
  selectedTabIndex: number;
}

export enum SettingType {
  RecordTypeFilter = 'typeFilter',
  RecordViewAutoscroll = 'autoscroll',
  SiteNumberFilter = 'siteNumberFilter',
  TestNumberFilter = 'testNumberFilter',
  TestTextFilter = 'testTextFilter',
  PassFailFilter = 'passFailFilter',
  ProgramFilter = 'programFilter',
  Yield = 'yield'
}
