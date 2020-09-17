import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordViewComponent } from './stdf-record-view.component';
import { StdfRecordComponent } from '../stdf-record/stdf-record.component';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { FormsModule } from '@angular/forms';
import { CheckboxComponent } from '../basic-ui-elements/checkbox/checkbox.component';
import { ButtonComponent } from '../basic-ui-elements/button/button.component';
import { MockServerService } from '../services/mockserver.service';
import { AppstateService } from '../services/appstate.service';
import * as constants from './../services/mockserver-constants';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';
import { StdfRecordType, StdfRecordEntryType, STDF_RECORD_TYPE_LONG_FORM } from '../stdf/stdf-stuff';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';

describe('StdfRecordViewComponent', () => {
  let component: StdfRecordViewComponent;
  let fixture: ComponentFixture<StdfRecordViewComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let appstateService: AppstateService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordViewComponent,
        StdfRecordComponent,
        CardComponent,
        CheckboxComponent,
        ButtonComponent,
      ],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer // key must be equal to the key define in interface AppState, i.e. userSettings
        })
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    appstateService = TestBed.inject(AppstateService);
    fixture = TestBed.createComponent(StdfRecordViewComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterAll(() => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)?.remove();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render message "No records available!" if appstate service does not have any record', () => {
    expect(appstateService.stdfRecords.length).toEqual(0, 'We expect no records for passing this test');
    expect(debugElement.queryAll(By.css('p')).some(e => (e.nativeElement.innerText as string).includes('No records available!')))
      .toEqual(true, 'No element containing text "No records available!" could be found');
  });

  // test for autoscroll, i.e. record view changes
  describe('autoscroll', () => {
    it('should be activated initially', () => {
      expect(component.autoScroll).toBeTrue();
    });

    it('should change current record automatically in case that a new record arrives', async () => {
      // generate changing results by using the mock server service
      let record1 = {
        type: 'PIR',
        HEAD_NUM: 0,
        SITE_NUM: 0
      };

      let record2 = {
        type: 'PIR',
        HEAD_NUM: 1,
        SITE_NUM: 1
      };

      mockServerService.setRepeatMessages(true);
      mockServerService.setMessages([
        {
          type: 'testresult',
          payload: [
            record1
          ]
        }]);

      let conditionRecord = (head: number, site: number) => {
        let record = debugElement.query(By.css('app-stdf-record'));
        let entries = record?.queryAll(By.css('.label'))
          .map(e => e.nativeElement.innerText);

        // check entries
        if (entries?.filter(e => e.includes('HEAD_NUM')).some(e => e.includes(head)))
          if (entries?.filter(e => e.includes('SITE_NUM')).some(e => e.includes(site)))
            return true;
        return false;
      };

      // wait until we can see the record1
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(0, 0),
        'Record "' + JSON.stringify(record1) + ' could not be found');

      // generate different record
      mockServerService.setMessages([
        {
          type: 'testresult',
          payload: [
            record2
          ]
        }]);

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(1, 1),
        'Record "' + JSON.stringify(record1) + ' could not be found');
    });
  });

  // record navigation, i.e. no autoscroll
  describe('navigation buttons', () => {
    it('should render navigation buttons "prev" and "next" if option autoscroll is turned off', async () => {
      // first we have to add some record(s) using the mock server service
      let record1 = {
        type: 'PIR',
        HEAD_NUM: 0,
        SITE_NUM: 0
      };

      let record2 = {
        type: 'PIR',
        HEAD_NUM: 1,
        SITE_NUM: 1
      };

      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        {
          type: 'testresult',
          payload: [
            record1,
            record2,
          ]
        },
        {
          // empty record, i.e. we stop sending new records
          // because the mock server service will repeat this last message
        }]);

      // wait until wee see the autoscroll checkbox
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => debugElement.queryAll(By.css('app-checkbox label'))
          .some(e => e.nativeElement.innerText.includes('Autoscroll')),
        'Autoscroll checkbox could not be found');

      // turn autoscroll off
      debugElement.queryAll(By.css('app-checkbox'))
        .filter(e => e.nativeElement.innerText.includes('Autoscroll'))[0]
        .query(By.css('.toggle')).nativeElement.click();

      let conditionRecord = (head: number, site: number) => {
        let record = debugElement.query(By.css('app-stdf-record'));
        let entries = record?.queryAll(By.css('.label'))
          .map(e => e.nativeElement.innerText);

        // check entries
        if (entries?.filter(e => e.includes('HEAD_NUM')).some(e => e.includes(head)))
          if (entries?.filter(e => e.includes('SITE_NUM')).some(e => e.includes(site)))
            return true;
        return false;
      };

      // we should see the last sent record, i.e. record2
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record2.HEAD_NUM, record2.SITE_NUM),
        'PIR with head ' + record2.HEAD_NUM + ' and site ' + record2.SITE_NUM + ' could not be found');

      // click prev button
      let prevButton = debugElement.query(By.css('#prev button')).nativeElement.click();

      // we should now see the first record, i.e. record1
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record1.HEAD_NUM, record1.SITE_NUM),
        'PIR with head ' + record1.HEAD_NUM + ' and site ' + record1.SITE_NUM + ' could not be found');
    });

    it('should have hidden class depending on the autoscroll state, i.e. hidden iff autoscroll is off', () => {
      // we need to simulate some record date is available, i.e.
      //  1. appstateservice must have some record
      //  2. add some record to component
      appstateService.stdfRecords.length = 1;
      // we need at least a single record in order to see the record navigation options and buttons
      let record1 = {
        type: StdfRecordType.Pir,
        values: [['HEAD_NUM', 0], ['SITE_NUM', 0]] as StdfRecordEntryType[]
      };
      (component as any).updateView([record1]);
      fixture.detectChanges();

      // check that next and prev button have hidden class
      expect(debugElement.queryAll(By.css('app-button'))
        .filter(e => e.nativeElement.innerText === 'prev' || e.nativeElement.innerText === 'next')
        .some(e => e.classes.hidden)).toEqual(true);

      // turn autoscroll off
      component.autoscrollChanged(false);
      fixture.detectChanges();

      // check that next and prev button DON'T have hidden class
      expect(debugElement.queryAll(By.css('app-button'))
        .filter(e => e.nativeElement.innerText === 'prev' || e.nativeElement.innerText === 'next')
        .some(e => e.classes.hidden)).toEqual(false);
    });
  });

  // filter only ptr
  describe('PTR Filter', () => {
    it('should be active initially', () => {
      let ptrRecord = component.recordTypeFilterCheckboxes.find(e => e.labelText === StdfRecordType.Ptr);
      expect(ptrRecord.checked).toBeTrue();
    });

    it('should not show PTRs if filter is not activated', async () => {
      let ptr = {
        type: 'PTR',
        HEAD_NUM: 0,
        SITE_NUM: 1
      };

      let pir = {
        type: 'PIR',
        HEAD_NUM: 0,
        SITE_NUM: 1
      };

      let ptrFilterCheckboxFound = () =>
        debugElement.queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .some(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr));

      // mock some arriving stdf records (ptr, pir) in order to make the
      // record filteres being shown
      mockServerService.setRepeatMessages(true);
      mockServerService.setMessages([
        {
          type: 'testresult',
          payload: [ptr, pir]
        }]);

      // wait for ptr record filter being shown
      await expectWaitUntil(
        () => fixture.detectChanges(),
        ptrFilterCheckboxFound,
        'PTR Filter could not be found');

      expect(component.filteredRecords.some(r => r.type === StdfRecordType.Ptr)).toBe(true, 'No PTRs found in filteredRecords');
      expect(component.filteredRecords.some(r => r.type === StdfRecordType.Pir)).toBe(true, 'No PIRs found in filteredRecords');

      // filter ptrs out
      component.recordTypeFilterChanged(false, StdfRecordType.Ptr);

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => component.filteredRecords.some(e => e.type === StdfRecordType.Pir) && !component.filteredRecords.some(e => e.type === StdfRecordType.Ptr),
        'Either unexpected PTR or no PIR could be found filteredRecords. Current filteredRecords: ' + JSON.stringify(component.filteredRecords));
    });
  });

  // filter too strong
  it('should render message "Filter settings are to restrictive! ' +
    'No records match the applied filter settings." if filter settings are too strong', async () => {
      // first we have to simulute some record
      //  1. appstateservice must have some record
      //  2. add some record to this component using updateView
      let priRecord = {
        type: StdfRecordType.Ptr,
        values: [['HEAD_NUM', 0], ['SITE_NUM', 0]] as StdfRecordEntryType[]
      };
      appstateService.stdfRecords = [priRecord];
      (component as any).applyFilters(false);
      fixture.detectChanges();

      // wait for ptr filter checkbox being checked
      await expectWaitUntil(
        null,
        () => debugElement.queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr))[0]
          .query(By.css('input')).nativeElement.checked,
        'PTR filter checkbox is not checked'
      );
      // set too strong filters by toggeling PTR and PIR filters
      debugElement.queryAll(By.css('app-checkbox'))
        .filter(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr))[0]
        .query(By.css('.toggle')).nativeElement.click();
      fixture.detectChanges();
      // wait for ptr filter checkbox being NOT checked
      await expectWaitUntil(
        null,
        () => debugElement.queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr))[0]
          .query(By.css('input')).nativeElement.checked !== true,
        'PTR filter checkbox is checked'
      );
      let filterTooStrongMessage = 'Filter settings are to restrictive! No records match the applied filter settings.';
      await expectWaitUntil(
        null,
        () => debugElement.queryAll(By.css('p')).some(e => e.nativeElement.innerText.includes(filterTooStrongMessage)),
        'PTR filter checkbox is checked'
      );
      // set too strong filters by toggeling PTR and PIR filters
      debugElement.queryAll(By.css('app-checkbox'))
        .filter(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr))[0]
        .query(By.css('.toggle')).nativeElement.click();
      fixture.detectChanges();
      // wait for ptr filter checkbox being checked
      await expectWaitUntil(
        null,
        () => debugElement.queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter(e => e.nativeElement.innerText.includes(StdfRecordType.Ptr))[0]
          .query(By.css('input')).nativeElement.checked,
        'PTR filter checkbox is not checked'
      );
      // wait PTR record element is located in current DOM
      await expectWaitUntil(
        null,
        () => {
          let recordText = debugElement.query(By.css('.stdfRecord')).nativeElement.innerText;
          if (recordText.includes(StdfRecordType.Ptr) && recordText.includes(STDF_RECORD_TYPE_LONG_FORM.PTR))
            return true;
          return false;
        },
        'PTR record canmnot be found on the page'
      );
    });
});
