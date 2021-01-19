import { Action, createReducer, on } from '@ngrx/store';
import { LotData } from '../models/lotdata.model';
import * as LotdataActions from 'src/app/actions/lotdata.actions';
import { MirRecord } from '../stdf/stdf-stuff';

const initialLotData: LotData = new MirRecord();

const reducer = createReducer(
  initialLotData,
  on(LotdataActions.updateLotData, (_state, {lotData}) => lotData)
);

export function lotdataReducer(state: LotData | undefined, action: Action) {
  return reducer(state, action);
}
