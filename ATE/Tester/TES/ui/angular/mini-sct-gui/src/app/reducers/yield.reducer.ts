import { Action, createReducer, on } from '@ngrx/store';
import { YieldData } from '../models/yield.model';
import * as YieldActions from 'src/app/actions/yield.actions';

export const initialYieldData: YieldData = [];

const reducer = createReducer(
  initialYieldData,
  on(YieldActions.updateYield, (_state, {yieldData}) => yieldData)
);

export function yieldReducer(state: YieldData | undefined, action: Action) {
  return reducer(state, action);
}