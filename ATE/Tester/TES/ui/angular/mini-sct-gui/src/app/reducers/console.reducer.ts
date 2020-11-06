import { ConsoleEntry } from './../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { createReducer, on, Action } from '@ngrx/store';

export const initialState = [];

const MAX_CONSOLE_ENTRIES = 4000;

const reducer = createReducer(
  initialState,
  on(ConsoleActions.addConsoleEntry, (state, {entries}) => {
      if (entries.length >= MAX_CONSOLE_ENTRIES) {
        return entries.slice(0, MAX_CONSOLE_ENTRIES);
      } else if (entries.length + state.length > MAX_CONSOLE_ENTRIES) {
        return [...entries, state.slice(0, MAX_CONSOLE_ENTRIES - entries.length)];
      } else {
        return [...entries,...state];
      }
    }),
  on(ConsoleActions.clearConsoleEntries, _state => [])
);

export function consoleReducer(state: ConsoleEntry[] | undefined, action: Action) {
  return reducer(state, action);
}