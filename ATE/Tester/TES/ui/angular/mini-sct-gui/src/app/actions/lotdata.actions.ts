import { props, createAction } from '@ngrx/store';
import { LotData } from '../models/lotdata.model';

const UPDATE_LOTDATA = '[LOTDATA] Update';

export const updateLotData = createAction(UPDATE_LOTDATA, props<{lotData: LotData}>());