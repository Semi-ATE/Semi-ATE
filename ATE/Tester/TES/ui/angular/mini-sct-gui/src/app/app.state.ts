import { Status } from './models/status.model';
import { ConsoleEntry } from './models/console.model';
import { StdfRecord, SiteHead } from 'src/app/stdf/stdf-stuff';
import { UserSettings } from './models/usersettings.model';
import { YieldData } from './models/yield.model';
import { createFeatureSelector, createSelector } from '@ngrx/store';
import { LotData } from './models/lotdata.model';
import { BinTableData } from './models/bintable.model';

export interface AppState {
  readonly systemStatus: Status;
  readonly results: Map<SiteHead, StdfRecord>;
  readonly consoleEntries: ConsoleEntry[];
  readonly userSettings: UserSettings;
  readonly connectionId: string;
  readonly yield: YieldData;
  readonly lotData: LotData;
  readonly binTable: BinTableData;
}

export const getDeviceId = createFeatureSelector<Status>('systemStatus');
export const selectDeviceId = createSelector(
  getDeviceId,
  (status: Status) => status.deviceId
);
