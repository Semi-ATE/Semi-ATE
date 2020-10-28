import * as ConnectionIdActions from './../actions/connectionid.actions';
import { createReducer, on, Action } from '@ngrx/store';

export const initialState = 'server_did_not_send_connection_id';

const reducer = createReducer(
  initialState,
  on(ConnectionIdActions.updateConnectionId, (_state, {connectionid}) => connectionid),
);

export function connectionIdReducer(state: string | undefined, action: Action) {
  return reducer(state, action);
}