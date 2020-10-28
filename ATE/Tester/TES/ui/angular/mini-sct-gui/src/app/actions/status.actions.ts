import { props, createAction } from '@ngrx/store';
import { Status } from './../models/status.model';

// Define the different action types
const UPDATE_STATUS = '[STATUS] Update';

// Define actions here
export const updateStatus = createAction(UPDATE_STATUS, props<{status: Status}>());
