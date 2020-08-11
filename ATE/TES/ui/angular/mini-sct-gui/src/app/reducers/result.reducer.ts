import { PartResult } from './../models/result.model'
import * as ResultActions from './../actions/result.actions'

// define the initial state here
const initialState: PartResult[] = [];

export function resultReducer(state: PartResult[] = initialState, action: ResultActions.Actions) {

  // return the new state (i.e. next state) depending on the current action type
  // and payload
  switch(action.type) {
    case ResultActions.ADD_RESULT:
        return [...state, action.payload];
    default:
        return state;
  }
}
