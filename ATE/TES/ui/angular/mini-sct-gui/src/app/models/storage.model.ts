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


export enum SettingType {
  RecordTypeFilter = 'typeFilter',
  RecordViewAutoscroll = 'autoscroll',
  SiteNumberFilter = 'siteNumberFilter',
  TestNumberFilter = 'testNumberFilter',
  TestTextFilter = 'testTextFilter',
  PassFailFilter = 'passFailFilter'
}

type settingType = RecordViewAutoscrollSetting | SiteNumberFilterSetting | RecordTypeFilterSetting | TestNumberFilterSetting;

export function generateDefaultSettings(type: SettingType): settingType {
  switch(type) {
    case SettingType.RecordTypeFilter:
      return {
        selectedTypes: ALL_STDF_RECORD_TYPES
      };
    case SettingType.SiteNumberFilter:
      return {
        enabled: false,
        selectedSites: ''
      };
    case SettingType.TestNumberFilter:
      return {
        enabled: false,
        selectedTestNumbers: ''
      };
    case SettingType.RecordViewAutoscroll:
      return {
        enabled: false
      };
  }
}

