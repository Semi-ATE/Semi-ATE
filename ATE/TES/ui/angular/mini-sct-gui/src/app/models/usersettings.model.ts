import { TestOptionValue } from '../system-control/test-option/test-option.component';

export enum TestOptionType {
  stopOnFail = 'stop_on_fail',
  singleStep = 'single_step',
  stopAtTestNumber = 'stop_on_test',
  triggerForTestNumber = 'trigger_on_test',
  triggerOnFailure = 'trigger_on_fail',
  triggerSiteSpecific = 'trigger_site_specific',
}

export interface TestOptionSetting {
  type: TestOptionType;
  value: TestOptionValue;
}

export interface UserSettings {
  testOptions: TestOptionSetting[];
}