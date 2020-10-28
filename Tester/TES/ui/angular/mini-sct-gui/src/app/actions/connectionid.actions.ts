import { props, createAction } from '@ngrx/store';

// Define the different action types
const UPDATE_CONNECTION_ID = '[CONN ID] Update';

// Define actions here
export const updateConnectionId = createAction(UPDATE_CONNECTION_ID, props<{connectionid: string}>());