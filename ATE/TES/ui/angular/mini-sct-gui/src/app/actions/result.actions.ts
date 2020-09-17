import { Action } from '@ngrx/store';
import { StdfRecord } from 'src/app/stdf/stdf-stuff';

// Define the different action types
export const ADD_RESULT = '[RESULT] Add';

// Define actions here
export class AddResult implements Action {
    readonly type = ADD_RESULT;
    constructor(public payload: StdfRecord) {}
}

// For a comfortable access all actions will be merged into a single type
export type Actions = AddResult;