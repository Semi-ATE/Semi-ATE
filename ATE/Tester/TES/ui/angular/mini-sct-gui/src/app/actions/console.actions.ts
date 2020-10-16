import { createAction, props } from '@ngrx/store';
import { ConsoleEntry } from './../models/console.model';

// Define the different action types
const ADD_CONSOLE = '[CONSOLE] Add';
const CLEAR_CONSOLE = '[CONSOLE] Clear';

export const addConsoleEntry = createAction(ADD_CONSOLE, props<{entries: ConsoleEntry[]}>());
export const clearConsoleEntries = createAction(CLEAR_CONSOLE);
