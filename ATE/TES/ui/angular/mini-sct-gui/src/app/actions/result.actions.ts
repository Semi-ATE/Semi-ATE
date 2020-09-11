import { createAction, props } from '@ngrx/store';
import { PrrRecord } from 'src/app/stdf/stdf-stuff';

// Define the different action types
const ADD_RESULT = '[RESULT] Add';

export const addResult = createAction(ADD_RESULT, props<{prr: PrrRecord}>());
