import { TestBed } from '@angular/core/testing';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { StdfRecordFilterService } from './stdf-record-filter.service';
import { AppstateService } from '../appstate.service';
import { StoreModule } from '@ngrx/store';
import { StdfRecordType } from 'src/app/stdf/stdf-stuff';
import { MockServerService } from '../mockserver.service';
import { yieldReducer } from 'src/app/reducers/yield.reducer';

describe('StdfRecordFilterService', () => {
  let service: StdfRecordFilterService;
  let mockServerService: MockServerService;
  let appstateService: AppstateService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
          yield: yieldReducer
        })
      ],
      declarations: [],
    });
    mockServerService = TestBed.inject(MockServerService);
    appstateService = TestBed.inject(AppstateService);
    service = TestBed.inject(StdfRecordFilterService);
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should inform when new results are available', () => {
    let updateFilteredRecordsSpy = spyOn<any>(service, 'updateFilteredRecords').and.callThrough();
    let nextSpy = spyOn(service.newResultsAvailable$, 'next');
    let records = [
      {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 1}]},
      {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 2}]},
      {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 3}]}
    ];
    appstateService.newRecordReceived$.next(records);
    expect(updateFilteredRecordsSpy).toHaveBeenCalled();
    expect(nextSpy).toHaveBeenCalled();
  });
});
