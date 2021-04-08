import { StdfRecordType } from '../stdf/stdf-stuff';
import { LogLevelString } from '../system-console/system-console.component';
import { LogLevel } from './usersettings.model';

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
export interface LotDataSetting {
  selectedTabIndex: number;
}
export interface LogLevelFilterSetting {
  logLevelFilter: Array<LogLevelString>;
}

export interface SourceFilterSetting {
  sourceFilter: string;
}

export interface ModalDialogFilterSetting {
  modalDialogFilter: Array<LogLevel>;
}

export enum SettingType {
  RecordTypeFilter = 'typeFilter',
  RecordViewAutoscroll = 'autoscroll',
  SiteNumberFilter = 'siteNumberFilter',
  TestNumberFilter = 'testNumberFilter',
  TestTextFilter = 'testTextFilter',
  PassFailFilter = 'passFailFilter',
  ProgramFilter = 'programFilter',
  Yield = 'yield',
  LotData =  'lotdata',
  LogLevelFilter = 'logLevelFilter',
  SourceFilter = 'sourceFilter',
  ModalDialogFilter = 'modalDialogFilter'
}
