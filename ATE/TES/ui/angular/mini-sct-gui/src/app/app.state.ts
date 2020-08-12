import { Status } from './models/status.model';
import { PartResult } from './models/result.model';
import { ConsoleEntry } from './models/console.model';

export interface AppState {
  readonly systemStatus: Status;
  readonly results: PartResult[];
  readonly consoleEntries: ConsoleEntry[];
}