import { TestOptionValue } from '../system-control/test-option/test-option.component';

export enum TestOptionType {
  stopOnFail = 'stop_on_fail',
  singleStep = 'single_step',
  stopAtTestNumber = 'stop_on_test',
  triggerForTestNumber = 'trigger_on_test',
  triggerOnFailure = 'trigger_on_fail',
  triggerSiteSpecific = 'trigger_site_specific',
}

export enum LogLevel {
  Debug = 10,
  Info = 20,
  Warning = 30,
  Error = 40
}

export interface TestOptionSetting {
  type: TestOptionType;
  value: TestOptionValue;
}

export interface UserSettings {
  testOptions: TestOptionSetting[];
  logLevel: LogLevel;
}
