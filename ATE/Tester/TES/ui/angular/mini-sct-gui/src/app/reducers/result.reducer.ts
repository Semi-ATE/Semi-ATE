import * as ResultActions from './../actions/result.actions';
import { SiteHead, computeSiteHeadFromRecord, PrrRecord } from '../stdf/stdf-stuff';
import { createReducer, on, Action } from '@ngrx/store';

// define the initial state here
export const initialState = new Map<SiteHead, PrrRecord>();

const reducer = createReducer(
  initialState,
  on(ResultActions.addResult, (state, {prr}) => {
    let key: SiteHead = computeSiteHeadFromRecord(prr);
    state.set(key, prr);
    return new Map<SiteHead, PrrRecord>(state);
  }),
  on(ResultActions.clearResult, _state => new Map<SiteHead, PrrRecord>())
);

export function resultReducer(state: Map<SiteHead, PrrRecord> | undefined, action: Action) {
  return reducer(state, action);
}
