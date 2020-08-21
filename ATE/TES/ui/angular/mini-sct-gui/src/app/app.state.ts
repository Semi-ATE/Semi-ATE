import { Status } from './models/status.model';
import { ConsoleEntry } from './models/console.model';
import { StdfRecord, SiteHead } from 'src/app/stdf/stdf-stuff';
import { UserSettings } from './models/usersettings.model';

export interface AppState {
  readonly systemStatus: Status;
  readonly results: Map<SiteHead, StdfRecord>;
  readonly consoleEntries: ConsoleEntry[];
  readonly userSettings: UserSettings;
}