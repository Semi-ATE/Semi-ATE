import { ConsoleEntry } from '../models/console.model';
import { consoleReducer } from './console.reducer';
import * as ConsoleActions from './../actions/console.actions';

describe('Console Reducer', () => {
  it('should not have contain console message in the beginning' ,() => {
    const EXPECTED_INITIAL_STATE = new Array<ConsoleEntry>();
    expect(consoleReducer(undefined, {type: 'foo'})).toEqual(EXPECTED_INITIAL_STATE);
  });

  it('should add console message to array' ,() => {
    const consoleEntry: ConsoleEntry = {
      date: '01.01.2001',
      description: 'Test description',
      source: 'Mock',
      type: 'Info',
      orderMessageId: undefined
    };

    const ENTRIES = new Array<ConsoleEntry>();
    for (let i = 0; i < 1000; ++i) {
      ENTRIES.push({...consoleEntry, orderMessageId: i});
    }
    const REDUCER_ADD_RESAULT = consoleReducer(undefined, ConsoleActions.addConsoleEntry({entries:ENTRIES}));
    expect(REDUCER_ADD_RESAULT).toEqual(ENTRIES);
  });

  it('should only insert the first and latest entries (max 4000)' ,() => {
    const consoleEntry: ConsoleEntry = {
      date: '01.01.2001',
      description: 'Test description',
      source: 'Mock',
      type: 'Info',
      orderMessageId: undefined
    };

    const ENTRIES = new Array<ConsoleEntry>();
    for (let i = 0; i < 8000; ++i) {
      ENTRIES.push({...consoleEntry, orderMessageId: i});
    }
    const REDUCER_ADD_RESAULT = consoleReducer(undefined, ConsoleActions.addConsoleEntry({entries:ENTRIES}));
    expect(REDUCER_ADD_RESAULT).toEqual(ENTRIES.filter(e => e.orderMessageId < 4000));
  });

  it('should clear all entries on clear action' ,() => {
    const consoleEntry: ConsoleEntry = {
      date: '01.01.2001',
      description: 'Test description',
      source: 'Mock',
      type: 'Info',
      orderMessageId: undefined
    };

    const REDUCER_CLEAR_RESAULT = consoleReducer([consoleEntry], ConsoleActions.clearConsoleEntries());
    expect(REDUCER_CLEAR_RESAULT).toEqual([]);
  });

  it ('should delete oldest console messages', () => {
    // insert 4000 values
    const consoleEntry: ConsoleEntry = {
      date: '01.01.2001',
      description: 'Test description',
      source: 'Mock',
      type: 'Info',
      orderMessageId: undefined
    };

    const ENTRIES = new Array<ConsoleEntry>();
    for (let i = 0; i < 4000; ++i) {
      ENTRIES.push({...consoleEntry, orderMessageId: i});
    }

    const ADDITIONAL_MESSAGE = {...consoleEntry, orderMessageId: 4000};

    // add one additional message
    const REDUCER_ADD_RESAULT = consoleReducer(ENTRIES, ConsoleActions.addConsoleEntry({entries:[ADDITIONAL_MESSAGE]}));

    // verify outcome
    expect(REDUCER_ADD_RESAULT.length).toBe(4000);
    expect(REDUCER_ADD_RESAULT[0]).toEqual(ADDITIONAL_MESSAGE);
    expect(REDUCER_ADD_RESAULT).not.toContain({...consoleEntry, orderMessageId: 3999});
  });
});