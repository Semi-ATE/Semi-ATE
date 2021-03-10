import { props, createAction } from '@ngrx/store';
import { BinTableData } from '../models/bintable.model';

const UPDATE_BIN_TABLE = '[BIN] Update';

export const updateTable = createAction(UPDATE_BIN_TABLE, props<{ binData: BinTableData }>());
