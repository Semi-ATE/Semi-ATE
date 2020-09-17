import { ConsoleEntry } from './../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { createReducer, on, Action } from '@ngrx/store';

export const initialState = [];

const reducer = createReducer(
  initialState,
  on(ConsoleActions.addConsoleEntry, (state, {entries}) => [...entries,...state]),
  on(ConsoleActions.clearConsoleEntries, state => [])
);

export function consoleReducer(state: ConsoleEntry[] | undefined, action: Action) {
  return reducer(state, action);
}