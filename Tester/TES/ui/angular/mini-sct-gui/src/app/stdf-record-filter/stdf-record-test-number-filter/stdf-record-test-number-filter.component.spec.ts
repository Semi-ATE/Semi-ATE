import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordTestNumberFilterComponent } from './stdf-record-test-number-filter.component';
import { StorageMap } from '@ngx-pwa/local-storage';
import { MockServerService } from 'src/app/services/mockserver.service';
import { AppstateService } from 'src/app/services/appstate.service';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { DebugElement } from '@angular/core';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { InputComponent } from 'src/app/basic-ui-elements/input/input.component';
import { expectWaitUntil } from 'src/app/test-stuff/auxillary-test-functions';
import { By } from '@angular/platform-browser';
import { StdfRecordType } from 'src/app/stdf/stdf-stuff';
import { TestNumberFilterSetting } from 'src/app/models/storage.model';

describe('StdfRecordTestNumberFilterComponent', () => {
  let component: StdfRecordTestNumberFilterComponent;
  let fixture: ComponentFixture<StdfRecordTestNumberFilterComponent>;
  let storage: StorageMap;
  let mockServerService: MockServerService;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordTestNumberFilterComponent,
        CheckboxComponent,
        InputComponent
      ],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
        }),
      ],
    })
    .compileComponents();
  }));

  beforeEach( async () => {
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    mockServerService = TestBed.inject(MockServerService);
    appStateService = TestBed.inject(AppstateService);
    filterService = TestBed.inject(StdfRecordFilterService);
    fixture = TestBed.createComponent(StdfRecordTestNumberFilterComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  async function waitProperInitialization() {
    let expectedLabelText = 'Show only the following tests';
    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.queryAll(By.css('label')).some(e => e.nativeElement.innerText === expectedLabelText),
      'Expected label text ' + expectedLabelText + ' was not found.'
    );
  }

  it('should show Pass/Fail Information initially', async () => {
    await waitProperInitialization();
  });

  it('should be deactivated in the very beginning', async () => {
    expect(component.testNumberCheckboxConfig.checked).toBeFalse();
  });

  it('should filter tests by provided numbers', async () => {
    await waitProperInitialization();

    let filterSetting = '12,61';

    let matchingRecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 12}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 12}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 61}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 61}]},
    ]];

    let notMatchinrecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 121}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 1}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 161}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 610}]},
    ]];

    let records = matchingRecords.concat(notMatchinrecords);

    // get records into our component
    appStateService.stdfRecords = records;
    filterService.filteredRecords = records;

    // activate filter
    debugElement.query(By.css('app-checkbox .toggle')).nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === 0,
      'Filtered records should match no record in the beginning'
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('app-input input')).nativeElement.hasAttribute('disabled'),
      'Disabled attribute is supposed to disapear when filter has been activated'
    );

    component.testNumberInputConfig.value = filterSetting;
    component.filterChanged();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === matchingRecords.length,
      'Filtered records should be equal to: ' + JSON.stringify(matchingRecords)
    );
  });

  describe('restoreSettings', () => {
    it('should deactivate test number filter', async (done) => {
      await waitProperInitialization();

      component.testNumberCheckboxConfig.checked = true;
      (component as any).restoreSettings();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !component.testNumberCheckboxConfig.checked,
        'Restore settings did not deactivate site filter' );
        done();
      });
    });

    it('should apply settings from storage', async (done) => {
      await waitProperInitialization();

      let setting: TestNumberFilterSetting = {
        enabled: true,
        selectedTestNumbers: '1-2,6-7'
      };

      storage.set((component as any).getStorageKey(), setting).subscribe( async () => {
        // test
        (component as any).restoreSettings();
        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => component.testNumberCheckboxConfig.checked === setting.enabled &&
            component.testNumberInputConfig.value === setting.selectedTestNumbers,
          'Restore settings did not apply settings from storage' );
        done();
      });
    });

    describe('testNumberFromString', () => {
      it('should return -1 in case of invalid input', () => {
        let testCase = {
          input: 'hallo',
          expectedResult: -1,
        };
        expect(
          (component as any).testNumberFromString(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case of negative input', () => {
        let testCase = {
          input: '-18',
          expectedResult: -1,
        };
        expect(
          (component as any).testNumberFromString(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case that the input is not a integer number provided as string', () => {
        let testCase = {
          input: '1.0',
          expectedResult: -1,
        };

        expect(
          (component as any).testNumberFromString(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return valid site number', () => {
        let testCase = {
          input: '17',
          expectedResult: 17,
        };

        expect(
          (component as any).testNumberFromString(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });
    });

    describe('testNumbersFromRange', () => {
      it('should return empty array, i.e. [] in case that the input is invalid', () => {
        let testCases = [
          {
            input: '1',  // invalid as '1' is not a range like '1-4'
            expectedResult: [],
          },
          {
            input: '3-1', // invalid as range should be ordered like '1-3'
            expectedResult: [],
          },
          {
            input: 'hallo', // invalid
            expectedResult: [],
          }
        ];

        testCases.forEach(t =>
          expect(
            (component as any).testNumbersFromRange(
              t.input,
            )
          ).toEqual(t.expectedResult));
      });

      it('should return valid site numbers', () => {
        let testCase = {
          input: '2-7',
          expectedResult: [2, 3, 4, 5, 6, 7],
        };

        expect(
          (component as any).testNumbersFromRange(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });
    });

    describe('computeTestNumbersOfInterest', () => {
      it('should return [] if input is ""', () => {
        let expectedResult = [];
        const EMPTY_STRING = '';
        let result = (component as any).computeTestNumbersOfInterest(EMPTY_STRING);
        expect(result).toEqual(expectedResult);
      });

      it('should return "undefined" in case of any error', () => {
        let testCase = {
          input: '1,b-3', // invalid because 'b-3' is not a valid range
          expectedResult: undefined,
        };

        expect(
          (component as any).computeTestNumbersOfInterest(
            testCase.input,
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return site numbers in case that the input is valid', () => {
        let testCases = [
          {
            input: '0,1',
            expectedResult: [0, 1],
          },
          {
            input: '3-4',
            expectedResult: [3, 4],
          },
          {
            input: '1,2,3,4-5,1-5',
            expectedResult: [1, 2, 3, 4, 5],
          }
        ];

        testCases.forEach(t =>
          expect(
            (component as any).computeTestNumbersOfInterest(
              t.input
            )
          ).toEqual(t.expectedResult));
      });
    });
});
