import { TestBed } from '@angular/core/testing';
import { CommunicationService } from './communication.service';
import { MockServerService } from './mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { MessageTypes, AppstateService } from './appstate.service';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import * as ConnectionIdReducer from 'src/app/reducers/connectionid.reducer';
import { Store, StoreModule } from '@ngrx/store';
import * as saveAsFunctions from 'file-saver';
import { AppState } from '../app.state';
import { yieldReducer } from '../reducers/yield.reducer';

describe('AppstateService', () => {

  let service: AppstateService;
  let communicationService: CommunicationService;
  let mockServerService: MockServerService;
  let store: Store<AppState>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
          connectionId: ConnectionIdReducer.connectionIdReducer,
          yield: yieldReducer
        })
      ],
      declarations: [],
    });
    mockServerService = TestBed.inject(MockServerService);
    communicationService = TestBed.inject(CommunicationService);
    store = TestBed.inject(Store);
    service = TestBed.inject(AppstateService);

  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  describe(MessageTypes.Testresults, () => {
    it('should set/sync all stored test results to the received results', async () => {
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([constants.TEST_RESULTS_SITE_1_AND_2]);

      let expectedNumberOfRecords = constants.TEST_RESULTS_SITE_1_AND_2.payload.reduce((a,c) => a + c.length, 0);

      await expectWaitUntil (
        null,
        () => {
          let stdfRecordsStoredOnService = service.stdfRecords.reduce((a,c) => a + c.length, 0);
          return stdfRecordsStoredOnService === expectedNumberOfRecords;
        },
        `Number of records (${service.stdfRecords.reduce((a,c) => a + c.length, 0)}) ` +
        `are not equal to the number of expected records (${expectedNumberOfRecords})`
      );

      mockServerService.setMessages([{type: 'testresults', payload: []}]);
      await expectWaitUntil (
        null,
        () => service.stdfRecords.length === 0,
        'Number of records should become 0 but is was ' + service.stdfRecords.length
      );
    });
  });

  describe(MessageTypes.Logfile, () => {
    it('should call saveAs when receiving a log file' , async () => {
      let saveAsCalled = false;
      spyOn<any>(saveAsFunctions, 'saveAs').and.callFake( () => {
        saveAsCalled = true;
      });
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.LOG_FILE
      ]);

      await expectWaitUntil (
        null,
        () => saveAsCalled,
        'Function saveAs was not called'
      );
    });
  });

  describe(MessageTypes.ConnectionId, () => {
    it('should dispatch message id to the store' , async () => {
      let args = [];
      spyOnStoreArguments(store, 'dispatch', args);
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.CONNECTION_ID
      ]);

      await expectWaitUntil (
        null,
        () => {
          let result = args[0]?.connectionid === constants.CONNECTION_ID.payload.connectionid;
          result = result && args[0]?.type === '[CONN ID] Update';
          return result;
        },
        'Connection ID was not dispatched to the store, i.e. connection id reducer was not called'
      );
    });
  });

  describe(MessageTypes.Yield, () => {
    it('should dispatch yield data to the store' , async () => {
      let args = [];
      const EXPECTED_YIELD_DATA = [];
      const YIELD_MESSAGE_FROM_SERVER = {
        type: MessageTypes.Yield,
        payload: EXPECTED_YIELD_DATA
      };

      spyOnStoreArguments(store, 'dispatch', args);

      (service as any).handleServerMessage(YIELD_MESSAGE_FROM_SERVER);

      await expectWaitUntil (
        null,
        () => {
          if ( args[0]?.type === '[YIELD] Update' ) {
            return true;
          }
          return false;
        },
        'Yield was not dispatched to the store, i.e. yield reducer was not called'
      );

      expect(args[0].yieldData).toEqual(jasmine.arrayWithExactContents(EXPECTED_YIELD_DATA));
    });
  });
});
