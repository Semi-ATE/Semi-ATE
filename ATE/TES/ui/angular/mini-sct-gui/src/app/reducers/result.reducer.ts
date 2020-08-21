import * as ResultActions from './../actions/result.actions';
import { StdfRecordType, StdfRecord, stdfGetValue, SiteHead, STDF_RECORD_ATTRIBUTES, computeSiteHeadFromRecord } from '../stdf/stdf-stuff';

// define the initial state here
const initialState: Map<SiteHead, StdfRecord> = new Map<SiteHead, StdfRecord>();

export function resultReducer(state: Map<SiteHead, StdfRecord> = initialState, action: ResultActions.Actions): Map<SiteHead, StdfRecord> {

  // return the new state (i.e. next state) depending on the current action type
  // and payload
  switch(action.type) {
    case ResultActions.ADD_RESULT:
      if(action.payload.type === StdfRecordType.Prr) {
        let key: SiteHead = computeSiteHeadFromRecord(action.payload);
        state.set(key, action.payload);
        return new Map<SiteHead, StdfRecord>(state);
      }
      return state;
    default:
      return state;
  }
}
