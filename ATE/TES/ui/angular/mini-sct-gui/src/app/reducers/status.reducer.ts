import { Status, SystemState } from 'src/app/models/status.model';
import * as StatusActions from 'src/app/actions/status.actions';

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

export function statusReducer(state: Status = initialState, action: StatusActions.Actions) {
  // return the new state (i.e. next state) depending on the current action type
  // and payload
  switch(action.type) {
    case StatusActions.UPDATE_STATUS:
      return action.payload;
    default:
      return state;
  }
}
