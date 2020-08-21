import { Action } from '@ngrx/store';
import { TestOptionSetting } from './../models/usersettings.model';

// Define the different action types
export const SET_TEST_OPTIONS = '[TEST OPTIONS] Set';

// Define actions here
export class Set implements Action {
  readonly type = SET_TEST_OPTIONS;
  constructor(public payload: TestOptionSetting[]) {}
}

// For a comfortable access all actions will be merged into a single type
export type Actions = Set;