import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordTypeFilterComponent } from './stdf-record-type-filter.component';
import { StdfRecordFilterService } from '../../services/stdf-record-filter-service/stdf-record-filter.service';
import { StdfRecordType, StdfRecord, ALL_STDF_RECORD_TYPES } from '../../stdf/stdf-stuff';
import { DebugElement } from '@angular/core';
import { AppstateService } from '../../services/appstate.service';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../../reducers/status.reducer';
import { resultReducer } from '../../reducers/result.reducer';
import { consoleReducer } from '../../reducers/console.reducer';
import { userSettingsReducer } from '../../reducers/usersettings.reducer';
import { By } from '@angular/platform-browser';
import { ButtonComponent } from '../../basic-ui-elements/button/button.component';
import { CheckboxComponent } from '../../basic-ui-elements/checkbox/checkbox.component';
import { MockServerService } from '../../services/mockserver.service';
import { expectWaitUntil } from '../../test-stuff/auxillary-test-functions';
import { StorageMap } from '@ngx-pwa/local-storage';

describe('StdfRecordTypeFilterComponent', () => {
  let mockServerService: MockServerService;
  let component: StdfRecordTypeFilterComponent;
  let fixture: ComponentFixture<StdfRecordTypeFilterComponent>;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;
  let storage: StorageMap;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordTypeFilterComponent,
        ButtonComponent,
        CheckboxComponent
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
    mockServerService = TestBed.inject(MockServerService);
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    appStateService = TestBed.inject(AppstateService);
    filterService = TestBed.inject(StdfRecordFilterService);
    fixture = TestBed.createComponent(StdfRecordTypeFilterComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    appStateService.ngOnDestroy();
    mockServerService.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // filter only ptr
  describe('PTR Filter', () => {
    it('should be active initially', () => {
      let ptrRecord = component.recordTypeFilterCheckboxes.find(
        (e) => e.labelText === StdfRecordType.Ptr
      );
      expect(ptrRecord.checked).toBeTrue();
    });

    it('should remove all PTRs from the array fileteredRecords of the StdfRecordFilterService', async () => {
      let ptr: StdfRecord = {
        type: StdfRecordType.Ptr,
        values: [
          {key: 'HEAD_NUM', value: 0},
          {key: 'SITE_NUM', value: 1}
        ]
      };

      let pir: StdfRecord = {
        type: StdfRecordType.Pir,
        values: [
          {key: 'HEAD_NUM', value: 0},
          {key: 'SITE_NUM', value: 1}
        ]
      };
      appStateService.stdfRecords = [[ptr,pir]];
      filterService.filteredRecords = [[ptr,pir]];
      component.recordTypeFilterChanged(false, StdfRecordType.Ptr);
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !filterService.filteredRecords.some(p => p.some(e => e.type === StdfRecordType.Ptr)),
        'There is still some entry containing PTR records.'
      );
      component.recordTypeFilterChanged(true, StdfRecordType.Ptr);
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => filterService.filteredRecords.some(p => p.some(e => e.type === StdfRecordType.Ptr)),
        'There is no entry containing some PTR record.'
      );
    });
  });

  describe('Buttons for STDF type filter', () => {
    describe('All-button', () => {
      it('should render All-button in DOM', () => {
        expect(debugElement.query(By.css('#allSelected')).nativeElement.innerText).toContain('All');
      });

      it('should call selectAllRecords function when clicked', () => {
        let spy = spyOn(component, 'selectAllRecords');
        component.allRecordsSelectedButtonConfig.disabled = false;
        fixture.detectChanges();
        debugElement.query(By.css('#allSelected button')).nativeElement.click();
        fixture.detectChanges();
        expect(spy).toHaveBeenCalled();
      });

      it('should call function selectRecords(true)', () => {
        let spy = spyOn(component as any, 'selectRecords');
        component.selectAllRecords();
        expect(spy).toHaveBeenCalledWith(true);
      });

      it('should set checked-status of all checkboxes to true', () => {
        let expected = ALL_STDF_RECORD_TYPES.map((e) => true);
        (component as any).selectRecords(true);
        expect(
          component.recordTypeFilterCheckboxes.map((e) => e.checked)
        ).toEqual(jasmine.arrayWithExactContents(expected));
      });

      it('should disable All-button', () => {
        component.selectAllRecords();
        expect(component.allRecordsSelectedButtonConfig.disabled).toEqual(true);
      });

      it('should enable None-button', () => {
        component.selectAllRecords();
        expect(component.noneRecordsSelectedButtonConfig.disabled).toEqual(
          false
        );
      });

      it('should update disabled-status', () => {
        let spy = spyOn(
          component as any,
          'setDisabledStatusRecordFilterButtons'
        );
        component.selectAllRecords();
        expect(spy).toHaveBeenCalled();
      });
    });

    describe('None-button', () => {
      it('should render None-button in DOM', () => {
        expect(debugElement.query(By.css('#noneSelected button')).nativeElement.innerText).toContain('None');
      });

      it('should call unselectAllRecords function when clicked', async () => {
        let spy = spyOn(component, 'unselectAllRecords');

        // wait until NONE-button is clickable, i.e. NOT disabled
        let buttonEnabled = () => {
          if (!debugElement.query(By.css('#noneSelected button')).nativeElement.hasAttribute('disabled'))
            return true;
          return false;
        };

        await expectWaitUntil(
          () => fixture.detectChanges(),
          buttonEnabled,
          'NONE-Button is not clickable, i.e. button is disabled',
          100,
          3000
        );

        debugElement.query(By.css('#noneSelected button')).nativeElement.click();
        fixture.detectChanges();
        expect(spy).toHaveBeenCalled();
      });

      it('should call function selectRecords(false)', () => {
        let spy = spyOn(component as any, 'selectRecords');
        component.unselectAllRecords();
        expect(spy).toHaveBeenCalledWith(false);
      });

      it('should set checked-status of all checkboxes to false', () => {
        let expected = ALL_STDF_RECORD_TYPES.map((e) => false);
        (component as any).selectRecords(false);
        expect(
          component.recordTypeFilterCheckboxes.map((e) => e.checked)
        ).toEqual(jasmine.arrayWithExactContents(expected));
      });

      it('should disable None-button', () => {
        component.unselectAllRecords();
        expect(component.noneRecordsSelectedButtonConfig.disabled).toEqual(
          true
        );
      });

      it('should enable All-button', () => {
        component.unselectAllRecords();
        expect(component.allRecordsSelectedButtonConfig.disabled).toEqual(
          false
        );
      });

      it('should update disabled-status', () => {
        let spy = spyOn(
          component as any,
          'setDisabledStatusRecordFilterButtons'
        );
        component.unselectAllRecords();
        expect(spy).toHaveBeenCalled();
      });
    });
  });

  describe('deselectRecordType', () => {
    it('should not change array "selectedRecordTypes" if called twice', async () => {
      // wait until component gets initialized
      await expectWaitUntil(
        null,
        () => (component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
        'Component did not initialize properly'
      );

      let recordType = StdfRecordType.Ptr;
      let recordTypesInitial = (component as any).selectedRecordTypes;

      (component as any).deselectRecordType(recordType);
      let recordTypesAfterFirstCall = (component as any).selectedRecordTypes;

      expect(recordTypesInitial).not.toEqual(recordTypesAfterFirstCall);

      (component as any).deselectRecordType(recordType);
      let recordTypesAfterSecondCall = (component as any).selectedRecordTypes;

      expect(recordTypesAfterFirstCall).toEqual(recordTypesAfterSecondCall);
    });
  });

  describe('restoreSettings', () => {
    it('should select all record types if not defined in local storage', async (done) => {
      // wait until component is initialized
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () =>(component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
        'Did not initialized properly' );

        // setup
      (component as any).selectedRecordTypes = [];
      storage.clear().subscribe( async () => {
        // test
        let selectAllRecordsSpy = spyOn(component, 'selectAllRecords').and.callThrough();
        expect((component as any).selectedRecordTypes.length).toBe(0);
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => (component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
          '' );
        expect(selectAllRecordsSpy).toHaveBeenCalled();
        done();
      });
    });
    it('should select all record types if not fully defined in local storage', async (done) => {
      // wait until component is initialized
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () =>(component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
        'Did not initialize properly' );
      // setup
      // set identifier
      (component as any).selectedRecordTypes = [];
      storage.set((component as any).getStorageKey(),{}).subscribe( async () => {
        // test
        let selectAllRecordsSpy = spyOn(component, 'selectAllRecords').and.callThrough();
        expect((component as any).selectedRecordTypes.length).toBe(0);
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => (component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
          '' );
        expect(selectAllRecordsSpy).toHaveBeenCalled();
        done();
      });
    });
    it('should apply settings from storage', async (done) => {
      // wait until component is initialized
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => (component as any).selectedRecordTypes.length === ALL_STDF_RECORD_TYPES.length,
        'Did not initialize properly');
      // setup
      // set identifier
      (component as any).selectedRecordTypes = [];
      storage.set((component as any).getStorageKey(), {
        selectedTypes: [StdfRecordType.Ptr]
      }).subscribe(async () => {
        // test
        expect((component as any).selectedRecordTypes.length).toBe(0);
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => (component as any).selectedRecordTypes.length === 1,
          'Stored settings have not been applied');
        expect((component as any).selectedRecordTypes).toEqual([StdfRecordType.Ptr]);
        done();
      });
    });
  });
});
