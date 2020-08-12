import { Action } from '@ngrx/store'
import { ConsoleEntry } from './../models/console.model'

// Define the different action types
export const ADD_CONSOLE = '[CONSOLE] Add';
export const CLEAR_CONSOLE = '[CONSOLE] Clear';

// Define actions here
export class Add implements Action {
  readonly type = ADD_CONSOLE;
  constructor(public payload: ConsoleEntry) {}
}

export class Clear implements Action {
  readonly type = CLEAR_CONSOLE;
  constructor() {}
}

// For a comfortable access all actions will be merged into a single type
export type Actions = Add | Clear;