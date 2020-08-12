import { Action } from '@ngrx/store'
import { Status } from './../models/status.model'

// Define the different action types
export const UPDATE_STATUS = '[STATUS] Update';

// Define actions here
export class UpdateStatus implements Action {
    readonly type = UPDATE_STATUS;
    constructor(public payload: Status) {}
}

// For a comfortable access all actions will be merged into a single type
export type Actions = UpdateStatus;