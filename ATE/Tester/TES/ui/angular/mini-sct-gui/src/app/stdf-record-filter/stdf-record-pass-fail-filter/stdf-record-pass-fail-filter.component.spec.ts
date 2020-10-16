import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordPassFailFilterComponent } from './stdf-record-pass-fail-filter.component';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { StorageMap } from '@ngx-pwa/local-storage';
import { MockServerService } from 'src/app/services/mockserver.service';
import { AppstateService } from 'src/app/services/appstate.service';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { DebugElement } from '@angular/core';
import { DropdownComponent } from 'src/app/basic-ui-elements/dropdown/dropdown.component';
import { expectWaitUntil } from 'src/app/test-stuff/auxillary-test-functions';
import { By } from '@angular/platform-browser';
import { StdfRecordType } from 'src/app/stdf/stdf-stuff';
import { PassFailFilterSetting } from 'src/app/models/storage.model';

describe('StdfRecordPassFailFilterComponent', () => {
  let component: StdfRecordPassFailFilterComponent;
  let fixture: ComponentFixture<StdfRecordPassFailFilterComponent>;
  let storage: StorageMap;
  let mockServerService: MockServerService;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordPassFailFilterComponent,
        CheckboxComponent,
        DropdownComponent,
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
    fixture = TestBed.createComponent(StdfRecordPassFailFilterComponent);
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
    let expectedLabelText = 'Pass/Fail Information';
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
    expect(component.passFailCheckboxConfig.checked).toBeFalse();
  });

  it('should only show pass tests if activated and configured for tests that pass', async () => {
    // we need some records with different site numbers
    let passRecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 0}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 0}]},
    ]];

    let failedRecords = [[
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 1}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 2}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 11}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 10}]},
      {type: StdfRecordType.Ptr, values: [{key: 'TEST_FLG', value: 8}]},
    ]];

    let records = passRecords.concat(failedRecords);

    // get records into our component
    appStateService.stdfRecords = records;
    filterService.filteredRecords = records;

    await waitProperInitialization();

    // activate filter
    debugElement.query(By.css('app-checkbox .toggle')).nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === failedRecords.length,
      'Filtered records should match the failed records'
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('app-dropdown.dropdox.disabled')),
      'Filtered records should match the failed records'
    );

    component.dropdownConfig.selectedIndex = 1;
    component.dropdownConfig.value = component.dropdownConfig.items[1].value;
    component.filterChanged();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => filterService.filteredRecords.length === passRecords.length,
      'Filtered records should match the passed records'
    );
  });

  describe('restoreSettings', () => {
    it('should deactivate site number filter', async (done) => {
      await waitProperInitialization();

      component.passFailCheckboxConfig.checked = true;
      (component as any).restoreSettings();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !component.passFailCheckboxConfig.checked,
        'Restore settings did not deactivate site filter' );
        done();
      });
    });

    it('should apply settings from storage', async (done) => {
      await waitProperInitialization();

      let setting: PassFailFilterSetting = {
        enabled: true,
        selectedIndex: 1
      };

      storage.set((component as any).getStorageKey(), setting).subscribe( async () => {
        // test
        (component as any).restoreSettings();
        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => component.passFailCheckboxConfig.checked === setting.enabled &&
            component.dropdownConfig.selectedIndex === setting.selectedIndex,
          'Restore settings did not apply settings from storage' );
        done();
      });
    });

});
