import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordTestTextFilterComponent } from './stdf-record-test-text-filter.component';
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
import { StdfRecordType } from 'src/app/stdf/stdf-stuff';
import { TestNumberFilterSetting, TestTextFilterSetting } from 'src/app/models/storage.model';
import { By } from '@angular/platform-browser';

describe('StdfRecordTestTextFilterComponent', () => {
  let component: StdfRecordTestTextFilterComponent;
  let fixture: ComponentFixture<StdfRecordTestTextFilterComponent>;
  let storage: StorageMap;
  let mockServerService: MockServerService;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordTestTextFilterComponent,
        CheckboxComponent,
        InputComponent,
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
    fixture = TestBed.createComponent(StdfRecordTestTextFilterComponent);
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
    let expectedLabelText = 'Value contained in TEST_TXT';
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
    expect(component.testTextCheckboxConfig.checked).toBeFalse();
  });

  it('should filter tests by provided text', async () => {
    let filterSetting = 'contained_string';

    let matchingRecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: 'Pref' + filterSetting + 'Suf'}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: filterSetting + 'Suf'}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: 'Pref'+ filterSetting }]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: filterSetting}]},
    ]];

    let notMatchinrecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: 'contained_str'}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: 'hello'}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: ''}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_TXT', value: 'contained-string'}]},
    ]];

    let records = matchingRecords.concat(notMatchinrecords);

    // get records into our component
    appStateService.stdfRecords = records;
    filterService.filteredRecords = records;

    await waitProperInitialization();

    // activate filter
    debugElement.query(By.css('app-checkbox .toggle')).nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === records.length,
      'Filtered records should match all record in the beginning'
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('app-input input')).nativeElement.hasAttribute('disabled'),
      'Disabled attribute is supposed to disapear when filter has been activated'
    );

    component.testTextInputConfig.value = filterSetting;
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

      component.testTextCheckboxConfig.checked = true;
      (component as any).restoreSettings();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !component.testTextCheckboxConfig.checked,
        'Restore settings did not deactivate site filter' );
        done();
    });

    it('should apply settings from storage', async (done) => {
      await waitProperInitialization();

      let setting: TestTextFilterSetting = {
        enabled: true,
        containedTestText: 'contained'
      };

      storage.set((component as any).getStorageKey(), setting).subscribe( async () => {
        // test
        (component as any).restoreSettings();
        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => component.testTextCheckboxConfig.checked === setting.enabled &&
            component.testTextInputConfig.value === setting.containedTestText,
          'Restore settings did not apply settings from storage' );
        done();
      });
    });
  });
});
