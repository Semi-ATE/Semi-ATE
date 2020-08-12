import { ConsoleEntry } from './../models/console.model'
import * as ConsoleActions from './../actions/console.actions'

export function consoleReducer(state: ConsoleEntry[] = [], action: ConsoleActions.Actions) {

  // return the new state (i.e. next state) depending on the current action type
  // and payload
  switch(action.type) {
    case ConsoleActions.ADD_CONSOLE:
        return [...state, action.payload];
      case ConsoleActions.CLEAR_CONSOLE:
        return [];
    default:
        return state;
  }
}