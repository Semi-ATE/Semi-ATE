import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { StoreModule } from '@ngrx/store';
import { StorageMap } from '@ngx-pwa/local-storage';
import * as constants from './../../services/mockserver-constants';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { InputComponent } from 'src/app/basic-ui-elements/input/input.component';
import { ProgramFilterSetting, SiteNumberFilterSetting } from 'src/app/models/storage.model';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { AppstateService } from 'src/app/services/appstate.service';
import { MockServerService } from 'src/app/services/mockserver.service';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { expectWaitUntil, expectWhile, wait } from 'src/app/test-stuff/auxillary-test-functions';
import { StdfRecordSiteNumberFilterComponent } from '../stdf-record-site-number-filter/stdf-record-site-number-filter.component';
import { ProgramPattern, StdfRecordProgramFilterComponent, TestResult } from './stdf-record-program-filter.component';
import { StdfRecordType } from 'src/app/stdf/stdf-stuff';

describe('StdfRecordProgramFilterComponent', () => {
  let component: StdfRecordProgramFilterComponent;
  let fixture: ComponentFixture<StdfRecordProgramFilterComponent>;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;
  let storage: StorageMap;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordProgramFilterComponent,
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
    fixture = TestBed.createComponent(StdfRecordProgramFilterComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  async function waitProperInitialization() {
    let expectedLabelText = 'Program Pattern';
    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.queryAll(By.css('label')).some(e => e.nativeElement.innerText === expectedLabelText),
      'Expected label text ' + expectedLabelText + ' was not found.'
    );
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should filter test program runs', async () => {
    await waitProperInitialization();

    let matchingRun = [
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 0}, {key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 1}, {key: 'TEST_FLG', value: 8}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 2}, {key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 3}, {key: 'TEST_FLG', value: 3}]}
    ];

    let notMatchingRun = [
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 0}, {key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 1}, {key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 2}, {key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_NUM', value: 3}, {key: 'TEST_FLG', value: 0}]}
    ];

    // get records into our component
    let records = [matchingRun, notMatchingRun];
    appStateService.stdfRecords = records;
    filterService.filteredRecords = records;

    // apply filter settings
    let programFilter = '(0,p) && (1,f) && (2,p) && (3,f)';
    component.testProgramCheckboxConfig.checked = true;
    component.testProgramInputConfig.value = programFilter;
    component.testProgramFilterChanged();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === 1,
      'Filter did not show any effect');
    expect(filterService.filteredRecords[0]).toEqual(jasmine.arrayWithExactContents(matchingRun));
  });

  describe('error message', () => {
    it('should not show any error message in the beginning', async () => {
      await waitProperInitialization();

      await expectWhile(
        () => fixture.detectChanges(),
        () => component.testProgramInputConfig.errorMsg === '',
        'There should not be any error message');
    });
    it('should show an error message in  case of invalid input', async () => {
      await waitProperInitialization();

      let invalidInput = 'invalid';

      // activate filter
      debugElement.query(By.css('app-checkbox .toggle')).nativeElement.click();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !component.testProgramInputConfig.disabled,
        'Filter did not become active'
      );

      // mock invalid input
      component.testProgramInputConfig.value = invalidInput;
      debugElement.query(By.css('app-input input')).nativeElement.dispatchEvent(new Event('change'));

      await expectWhile(
        () => fixture.detectChanges(),
        () => component.testProgramInputConfig.errorMsg !== '',
        'There should be an error message');
    });

  });

  describe('testProgramFilterChanged', () => {
    it('should save the current filter settings', () => {
      let saveSettingsSpy = spyOn<any>(component, 'saveSettings');
      component.testProgramFilterChanged();
      expect(saveSettingsSpy).toHaveBeenCalled();
    });

    it('should publish new filter settings', () => {
      let updateFilterAndPublishSpy = spyOn<any>(component, 'updateFilterAndPublish');
      component.testProgramFilterChanged();
      expect(updateFilterAndPublishSpy).toHaveBeenCalled();
    });
  });

  describe( 'extractTestResult' , () => {
    it('should return undefined in case of invalid input', () => {
      let testCases = [
        {input: '(30,h)', expectedResult: undefined},
        {input: '(kds,passed)', expectedResult: undefined},
        {input: '30,true)', expectedResult: undefined},
        {input: '(10hz,fail)', expectedResult: undefined},
        {input: '(30,Fail', expectedResult: undefined},
        {input: '[30,pass]', expectedResult: undefined},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        expect((component as any).extractTestResult(testCases[idx].input)).toBe(undefined, 'Input: "' + testCases[idx].input + '" should not be accepted');
      }
    });

    it('should return expected test result in case valid input', () => {
      let testCases = [
        {input: '(30,pass)', expectedTestNumber: 30, expectedPassed: true},
        {input: ' (  30  ,  PASS)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, true)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30,True)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, T)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, t)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, passed)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, PaSS)', expectedTestNumber: 30, expectedPassed: true},
        {input: '(30, fail)', expectedTestNumber: 30, expectedPassed: false},
        {input: ' (  30  ,  FAILED)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30, false)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30,False)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30, F)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30, f)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30, failed)', expectedTestNumber: 30, expectedPassed: false},
        {input: '(30, FaIl)', expectedTestNumber: 30, expectedPassed: false},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        let result = (component as any).extractTestResult(testCases[idx].input) as TestResult;
        expect(result.passed).toEqual(testCases[idx].expectedPassed);
        expect(result.testNumber).toEqual(testCases[idx].expectedTestNumber);
      }
    });
  });

  describe( 'extractPattern' , () => {
    it('should return undefined in case of invalid input', () => {
      let testCases = [
        {input: '(30,h) && (hdh)', expectedResult: undefined},
        {input: 'Hallo', expectedResult: undefined},
        {input: '(,F) && (,P)', expectedResult: undefined},
        {input: '(10hz,fail)', expectedResult: undefined},
        {input: '(30,Fail', expectedResult: undefined},
        {input: '[30,pass]', expectedResult: undefined},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        expect((component as any).extractPattern(testCases[idx].input)).not.toBeDefined();
      }
    });

    it('should return expected test result in case valid input', () => {
      let testCases = [
        {input: '(30,pass)', expectedPattern: [{testNumber:30, passed:true}]},
        {input: '(330, P) && (123, fail)', expectedPattern: [{testNumber:330, passed:true}, {testNumber:123, passed:false}]},
        {input: '(330, P) && (123, fail)', expectedPattern: [{testNumber:330, passed:true}, {testNumber:123, passed:false}]},
        {input: '(434567, false)    && (330, P) && (123, fail)', expectedPattern: [{testNumber:434567, passed:false},{testNumber:330, passed:true}, {testNumber:123, passed:false}]},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        let result = (component as any).extractPattern(testCases[idx].input) as ProgramPattern;
        let satisfied = result.pattern.every(e => testCases[idx].expectedPattern.some(f => f.testNumber === e.testNumber && f.passed === e.passed));
        expect(satisfied).toBe(true, `${JSON.stringify(result.pattern)} does not contain all expected entries (${JSON.stringify(testCases[idx].expectedPattern)})`);
      }
    });
  });

  describe('extractAllPattern', () => {
    it('should return expected patterns in case of valid input', () => {
      let testCases = [
        {input: '(30,pass) && (17,t) || (4,F) && (301, failed)',
         expectedPatterns: [
           [{testNumber:30, passed:true}, {testNumber:17, passed:true}],
           [{testNumber:4, passed:false}, {testNumber:301, passed:false}],
        ]},
        {input: ' (  117, fail)',
         expectedPatterns: [
           [{testNumber:117, passed:false}],
        ]},
        {input: '      ',
         expectedPatterns: [
        ]},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        let result = (component as any).extractAllPattern(testCases[idx].input) as Array<ProgramPattern>;
        let satisfied = result.every(p => testCases[idx].expectedPatterns.some(ep => ep.every( er => p.pattern.some(r => r.passed === er.passed && r.testNumber === er.testNumber))));
        expect(satisfied).toBe(true, `${JSON.stringify(result)} does not contain all expected entries (${JSON.stringify(testCases[idx].expectedPatterns)})`);
      }
    });

    it('should return undefined in case of invalid input', () => {
      let testCases = [
        {input: 'hallo'},
        {input: '(30,pass) && (17,t) || (4,F) && (301,??)'},
        {input: '((300,T) && (200,failed))'},
      ];

      for(let idx = 0; idx < testCases.length; ++idx) {
        let result = (component as any).extractAllPattern(testCases[idx].input) as Array<ProgramPattern>;
        expect(result).not.toBeDefined();
      }
    });
  });

  describe('restoreSettings', () => {
    it('should deactivate program filter', async (done) => {
      await waitProperInitialization();

      // we mock some system state and wait until the component applied thsi state
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
      ]);

      // setup
      component.testProgramCheckboxConfig.checked = true;
      storage.clear().subscribe( async () => {
        // test
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => !component.testProgramCheckboxConfig.checked,
          'Restore settings did not deactivate site filter' );
        done();
      });
    });
    it('should apply settings from storage', async (done) => {
      await waitProperInitialization();
      // we mock some system state and wait until the component applied thsi state
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
      ]);

      // wait until status is ready
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => (component as any).deviceId === constants.MESSAGE_WHEN_SYSTEM_STATUS_READY.payload.device_id,
        'Device ID was not set');

      // setup
      let setting: ProgramFilterSetting = {
        enabled: true,
        value: '(1,f)'
      };
      storage.set((component as any).getStorageKey(), setting).subscribe( async () => {
        // test
        (component as any).restoreSettings();
        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => {
            let result = component.testProgramCheckboxConfig.checked === setting.enabled &&
            component.testProgramInputConfig.value === setting.value;
            return result;
          },
          'Restore settings did not apply settings from storage' );
        done();
      });
    });
  });
});
