import { Status, SystemState } from 'src/app/models/status.model';
import * as StatusActions from 'src/app/actions/status.actions';
import { Action, createReducer, on } from '@ngrx/store';

// define the initial state here
const initialState: Status = {
  deviceId: 'connecting',
  env: 'connecting',
  handler: 'connecting',
  time: 'connecting',
  sites: new Array<string>(),
  program: '',
  log: '',
  state: SystemState.connecting,
  reason: '',
  lotNumber: ''
};

const reducer = createReducer(
  initialState,
  on(StatusActions.updateStatus, (_state, {status}) => status)
);

export function statusReducer(state: Status | undefined, action: Action) {
  return reducer(state, action);
}
