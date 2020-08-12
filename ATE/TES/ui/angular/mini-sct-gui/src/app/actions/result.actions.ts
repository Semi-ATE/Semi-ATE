import { Action } from '@ngrx/store'
import { PartResult } from './../models/result.model'

// Define the different action types
export const ADD_RESULT = '[RESULT] Add';

// Define actions here
export class AddResult implements Action {
    readonly type = ADD_RESULT;
    constructor(public payload: PartResult) {}
}

// For a comfortable access all actions will be merged into a single type
export type Actions = AddResult;