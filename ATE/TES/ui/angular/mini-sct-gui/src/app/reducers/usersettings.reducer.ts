import { UserSettings, TestOptionSetting, TestOptionType } from 'src/app/models/usersettings.model';
import * as UserSettingsActions from 'src/app/actions/usersettings.actions';

let computeInitialState = () => {
  let settings: UserSettings = {
    testOptions: []
  };
  for (let e in TestOptionType) {
    if (!e)
      continue;
    settings.testOptions.push(
      {
        type: e,
        value: {
          active: false,
          value: -1
        }
      } as TestOptionSetting
    );
  }
  return settings;
};

// define the initial state here
const initialState = computeInitialState();

export function userSettingsReducer(usersettings: UserSettings = initialState, action: UserSettingsActions.Actions) {
  // return the new state (i.e. next state) depending on the current action type
  // and payload
  switch (action.type) {
    case  UserSettingsActions.SET_TEST_OPTIONS:
      return {testOptions: action.payload} as UserSettings;
    default:
      return usersettings;
  }
}