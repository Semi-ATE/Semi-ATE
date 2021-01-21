import { createAction, props } from '@ngrx/store';
import { PrrRecord } from 'src/app/stdf/stdf-stuff';

// Define the different action types
const ADD_RESULT = '[RESULT] Add';
const CLEAR_RESULT = '[RESULT] Clear';

export const addResult = createAction(ADD_RESULT, props<{prr: PrrRecord}>());
export const clearResult = createAction(CLEAR_RESULT);
