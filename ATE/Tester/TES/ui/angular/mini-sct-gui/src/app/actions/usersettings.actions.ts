import { createAction, props } from '@ngrx/store';
import { UserSettings } from './../models/usersettings.model';

// Define the different action types
const SET_TEST_OPTIONS = '[TEST OPTIONS] Set';

export const setSettings = createAction(SET_TEST_OPTIONS, props<UserSettings>());
