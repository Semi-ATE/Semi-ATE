import { UserSettings, TestOptionSetting, TestOptionType } from 'src/app/models/usersettings.model';
import * as UserSettingsActions from 'src/app/actions/usersettings.actions';
import { on, Action, createReducer } from '@ngrx/store';

let computeInitialState = () => {
  let settings: UserSettings = {
    testOptions: []
  };
  Object.keys(TestOptionType).forEach(e => {
    settings.testOptions.push(
      {
        type: e,
        value: {
          active: false,
          value: -1
        }
      } as TestOptionSetting);
  });
  return  settings;
};

// define the initial state here
const initialState = computeInitialState();

const reducer = createReducer(
  initialState,
  on(UserSettingsActions.setSettings, (state, {settings}) => {
    return {testOptions: settings};
  })
);

export function userSettingsReducer(state: UserSettings | undefined, action: Action) {
  return reducer(state, action);
}