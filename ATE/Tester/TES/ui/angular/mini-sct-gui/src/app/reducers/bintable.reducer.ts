import * as BinTableActions from '../actions/bintable.actions';
import { BinTableData } from '../models/bintable.model';
import { createReducer, on, Action } from '@ngrx/store';

export const initialState: BinTableData = [];

const reducer = createReducer(
  initialState,
  on(BinTableActions.updateTable, (_state, { binData }) => binData)
);

export function binReducer(state: BinTableData | undefined, action: Action) {
  return reducer(state, action);
}
