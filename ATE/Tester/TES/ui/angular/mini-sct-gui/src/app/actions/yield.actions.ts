import { props, createAction } from '@ngrx/store';
import { YieldData } from './../models/yield.model';

const UPDATE_YIELD = '[YIELD] Update';

export const updateYield = createAction(UPDATE_YIELD, props<{yieldData: YieldData}>());
