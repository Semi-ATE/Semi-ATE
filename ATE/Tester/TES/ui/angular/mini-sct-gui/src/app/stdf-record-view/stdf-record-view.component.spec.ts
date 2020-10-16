import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordViewComponent } from './stdf-record-view.component';
import { StdfRecordComponent } from '../stdf-record/stdf-record.component';
import { StoreModule, Store } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { FormsModule } from '@angular/forms';
import { CheckboxComponent } from '../basic-ui-elements/checkbox/checkbox.component';
import { ButtonComponent } from '../basic-ui-elements/button/button.component';
import { MockServerService } from '../services/mockserver.service';
import { AppstateService } from '../services/appstate.service';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { StdfRecordType } from '../stdf/stdf-stuff';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { InputComponent } from '../basic-ui-elements/input/input.component';
import { CommunicationService } from '../services/communication.service';
import { StdfRecordFilterService } from '../services/stdf-record-filter-service/stdf-record-filter.service';
import { StdfRecordTypeFilterComponent } from '../stdf-record-filter/stdf-record-type-filter/stdf-record-type-filter.component';
import { StdfRecordSiteNumberFilterComponent } from '../stdf-record-filter/stdf-record-site-number-filter/stdf-record-site-number-filter.component';
import { StorageMap } from '@ngx-pwa/local-storage';
import { StdfRecordTestTextFilterComponent } from '../stdf-record-filter/stdf-record-test-text-filter/stdf-record-test-text-filter.component';
import { StdfRecordTestNumberFilterComponent } from '../stdf-record-filter/stdf-record-test-number-filter/stdf-record-test-number-filter.component';
import { StdfRecordPassFailFilterComponent } from '../stdf-record-filter/stdf-record-pass-fail-filter/stdf-record-pass-fail-filter.component';
import { DropdownComponent } from '../basic-ui-elements/dropdown/dropdown.component';
import { StdfRecordProgramFilterComponent } from '../stdf-record-filter/stdf-record-program-filter/stdf-record-program-filter.component';
import { SystemBinStatusComponent } from '../system-bin-status/system-bin-status.component';

describe('StdfRecordViewComponent', () => {
  let component: StdfRecordViewComponent;
  let fixture: ComponentFixture<StdfRecordViewComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let appstateService: AppstateService;
  let communicationService: CommunicationService;
  let filterService: StdfRecordFilterService;
  let storage: StorageMap;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordViewComponent,
        StdfRecordComponent,
        CardComponent,
        CheckboxComponent,
        ButtonComponent,
        InputComponent,
        DropdownComponent,
        StdfRecordTypeFilterComponent,
        StdfRecordSiteNumberFilterComponent,
        StdfRecordTestTextFilterComponent,
        StdfRecordTestNumberFilterComponent,
        StdfRecordPassFailFilterComponent,
        StdfRecordTestNumberFilterComponent,
        StdfRecordProgramFilterComponent,
        SystemBinStatusComponent
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
    }).compileComponents();
  }));

  beforeEach( async () => {
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    mockServerService = TestBed.inject(MockServerService);
    communicationService = TestBed.inject(CommunicationService);
    appstateService = TestBed.inject(AppstateService);
    filterService = TestBed.inject(StdfRecordFilterService);
    fixture = TestBed.createComponent(StdfRecordViewComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    mockServerService.ngOnDestroy();
  });

  // some helper function for finding stdf records
  let conditionRecord = (head: number, site: number) => {
    let record = debugElement.query(By.css('app-stdf-record'));
    let entries = record
      ?.queryAll(By.css('.label'))
      .map((e) => e.nativeElement.innerText);

    // check entries
    if (entries?.filter((e) => e.includes('HEAD_NUM')).some((e) => e.includes(head)))
      if (entries?.filter((e) => e.includes('SITE_NUM')).some((e) => e.includes(site)))
        return true;
    return false;
  };

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render message "No records available!" if appstate service does not have any record', async () => {
    expect(appstateService.stdfRecords.length).toEqual(0,'We expect no records for passing this test' );

    // wait for the expected message
    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.queryAll(By.css('p')).some((e) => (e.nativeElement.innerText as string).includes('No records available!')),
      'No element containing text "No records available!" could be found'
    );
  });

  it('should get currentRecordIndex as 0 if no Records are filtered', () => {
    filterService.filteredRecords = [];
    (component as any).updateView();
    expect((component as any).currentRecordIndex).toEqual([0,0]);
  });

  describe('currentRecord', () => {
    it('should return Unknown Ptr in case of an invalid index', () => {
      // generate invalid index
      (component as any).currentRecordIndex = [0,0];
      filterService.filteredRecords = [];
      let expectedResult = { type: StdfRecordType.Unknown, values: [] };
      let result = component.currentRecord();
      expect(result.type).toEqual(expectedResult.type);
      expect(result.values.length).toEqual(0);
    });
  });

  // test for autoscroll, i.e. record view changes
  describe('autoscroll', () => {
    it('should be activated initially, i.e. if there are no settings stored in local storage', async () => {
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => component.autoscrollCheckboxConfig.checked,
        'Autoscroll must be checked'
      );
    });

    it('should change current record automatically in case that a new record arrives', async () => {
      // generate changing results by using the mock server service
      let record1 = {type: 'PIR', HEAD_NUM: 0, SITE_NUM: 0};
      let record2 = {type: 'PIR', HEAD_NUM: 1, SITE_NUM: 1};
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        {type: 'testresult', payload: [record1]},
        {}
      ]);

      // wait until we can see the record1
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record1.HEAD_NUM, record1.SITE_NUM),
        'Record "' + JSON.stringify(record1) + ' could not be found');

      // generate next record
      mockServerService.setMessages([
        {type: 'testresult', payload: [record2] }
      ]);
      // wait until we can see the record2
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record2.HEAD_NUM, record2.SITE_NUM),
        'Record "' + JSON.stringify(record2) + ' could not be found');
    });

    it('should set currentRecordIndex to the last index of array filteredRecords', () => {
      // add two records
      let records = [[
        {type: StdfRecordType.Pir, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]},
        {type: StdfRecordType.Prr, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]}
      ]];
      expect((component as any).currentRecordIndex).toEqual([0,0]);
      filterService.filteredRecords = records;
      appstateService.stdfRecords = records;
      (component as any).updateView();
      fixture.detectChanges();
      expect((component as any).currentRecordIndex).toEqual([0,1]);
    });

    it('should not decrement currentRecordIndex if it is 0', () => {
      (component as any).currentRecordIndex = 0;
      component.previousRecord();
      expect((component as any).currentRecordIndex).toEqual(0);
    });
  });

  // record navigation, i.e. no autoscroll
  describe('navigation buttons', () => {
    it('should render navigation buttons "prev" and "next" if option autoscroll is turned off', async () => {
      // first we have to add some record(s) using the mock server service
      let record1 = {type: 'PIR', HEAD_NUM: 0, SITE_NUM: 0 };
      let record2 = {type: 'PIR', HEAD_NUM: 1, SITE_NUM: 1 };

      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        {type: 'testresult', payload: [record1, record2]},
      ]);

      // wait until autoscroll is checked
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => component.autoscrollCheckboxConfig.checked,
        'Autoscroll must be checked'
      );

      // wait for record2
      // wait until we can see the record2
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record2.HEAD_NUM, record2.SITE_NUM),
        'Record "' + JSON.stringify(record2) + ' could not be found' );

      // wait until wee see the autoscroll checkbox
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () =>
          debugElement
            .queryAll(By.css('app-checkbox label'))
            .some((e) => e.nativeElement.innerText.includes('Autoscroll')),
        'Autoscroll checkbox could not be found' );

      let autoscrollChanged = spyOn(component, 'autoscrollChanged').and.callThrough();

      // turn autoscroll off
      debugElement
        .queryAll(By.css('app-checkbox'))
        .find((e) => e.nativeElement.innerText.includes('Autoscroll'))
        .query(By.css('.toggle'))
        .nativeElement.click();

      expect(autoscrollChanged).toHaveBeenCalledWith(false);

      let enabledPrevButton = () => {
        if (debugElement.query(By.css('#prev')).classes.hidden)
          return false;
        if (!debugElement.query(By.css('#prev button'))?.nativeElement.hasAttribute('disabled'))
          return true;
        return false;
      };

      await expectWaitUntil(
        () => fixture.detectChanges(),
        enabledPrevButton,
        'Prev-button could not be found or it is disabled');

      // click prev button
      let prevButton = debugElement
        .query(By.css('#prev button'))
        .nativeElement.click();

      // we should now see the first record, i.e. record1
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => conditionRecord(record1.HEAD_NUM, record1.SITE_NUM),
        'PIR with head ' +
          record1.HEAD_NUM +
          ' and site ' +
          record1.SITE_NUM +
          ' could not be found'
      );
    });

    it('should have hidden class depending on the autoscroll state, i.e. hidden if autoscroll is off', () => {
      // we need to simulate some record date is available, i.e.
      let stdfRecord = { type: StdfRecordType.Pir, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]};
      filterService.filteredRecords = [[stdfRecord]];
      appstateService.stdfRecords = [[stdfRecord]];
      // we need at least a single record in order to see the record navigation options and buttons
      (component as any).updateView();
      fixture.detectChanges();

      // check that next and prev button have hidden class
      expect(
        debugElement
          .queryAll(By.css('app-button'))
          .filter(
            (e) =>
              e.nativeElement.innerText === 'prev' ||
              e.nativeElement.innerText === 'next'
          )
          .some((e) => e.classes.hidden)
      ).toEqual(true);

      // turn autoscroll off
      component.autoscrollCheckboxConfig.checked = false;
      component.autoscrollChanged(false);
      fixture.detectChanges();

      // check that next and prev button DON'T have hidden class
      expect(
        debugElement
          .queryAll(By.css('app-button'))
          .filter(
            (e) =>
              e.nativeElement.innerText === 'prev' ||
              e.nativeElement.innerText === 'next'
          )
          .some((e) => e.classes.hidden)
      ).toEqual(false);
    });

    describe('nextRecord', () => {
      it('should not increment currentRecordIndex iff currentRecordIndex is equal to the length of array filteredRecords', () => {
        // add two records
        let records = [[
          {type: StdfRecordType.Pir, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]},
          {type: StdfRecordType.Prr, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]}
        ]];
        filterService.filteredRecords = records;
        appstateService.stdfRecords = records;
        (component as any).updateView();
        fixture.detectChanges();

        expect((component as any).currentRecordIndex).toEqual([0,1]);
        let oldIndex = (component as any).currentRecordIndex;
        component.nextRecord();
        expect((component as any).currentRecordIndex).toEqual(oldIndex);
      });

      it('should increment "currentRecordIndex" iff "currentRecordIndex" is not pointing to the end of the array "filteredRecords".', () => {
        let records = [[
          {type: StdfRecordType.Pir, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]},
          {type: StdfRecordType.Prr, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]}
        ]];
        component.autoscrollCheckboxConfig.checked = false;
        component.autoscrollChanged(false);
        (component as any).updateView();
        fixture.detectChanges();

        // mock some records
        filterService.filteredRecords = records;
        appstateService.stdfRecords = records;
        const oldIndex = [...(component as any).currentRecordIndex];
        component.nextRecord();
        expect((component as any).currentRecordIndex).toEqual([oldIndex[0], oldIndex[1] + 1]);
      });
    });
  });

  // filter too strong
  it('should render message "Filter settings are too restrictive! No records match the applied filter settings." if filter settings are too strong', async () => {
    let records = [[
      {type: StdfRecordType.Pir, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]},
      {type: StdfRecordType.Prr, values: [{key: 'HEAD_NUM', value: 0}, {key: 'SITE_NUM', value: 0}]}
    ]];
    filterService.filteredRecords = records;
    appstateService.stdfRecords = records;
    (component as any).updateView();
    fixture.detectChanges();

    // wait for ptr filter checkbox being checked
    await expectWaitUntil(
      null,
      () =>
        debugElement
          .queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter((e) =>
            e.nativeElement.innerText.includes(StdfRecordType.Ptr)
          )[0]
          .query(By.css('input')).nativeElement.checked,
      'PTR filter checkbox is not checked'
    );
    // set too strong filters by toggeling PIR and PRR filters
    debugElement
      .queryAll(By.css('app-checkbox'))
      .filter((e) => e.nativeElement.innerText.includes(StdfRecordType.Pir))[0]
      .query(By.css('.toggle'))
      .nativeElement.click();
    debugElement
      .queryAll(By.css('app-checkbox'))
      .filter((e) => e.nativeElement.innerText.includes(StdfRecordType.Prr))[0]
      .query(By.css('.toggle'))
      .nativeElement.click();
    fixture.detectChanges();

    // wait for PIR- and PRR-filter checkbox being NOT checked
    await expectWaitUntil(
      null,
      () =>
        debugElement
          .queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter((e) =>
            e.nativeElement.innerText.includes(StdfRecordType.Pir)
          )[0]
          .query(By.css('input')).nativeElement.checked !== true &&
        debugElement
          .queryAll(By.css('.stdfRecordTypes app-checkbox'))
          .filter((e) =>
            e.nativeElement.innerText.includes(StdfRecordType.Prr)
          )[0]
          .query(By.css('input')).nativeElement.checked !== true
        ,
      'PIR and PRR filter checkbox is checked'
    );
    let filterTooStrongMessage =
      'Filter settings are too restrictive! No records match the applied filter settings.';

    await expectWaitUntil(
      null,
      () =>
        debugElement
          .queryAll(By.css('p'))
          .some((e) =>
            e.nativeElement.innerText.includes(filterTooStrongMessage)
          ),
      `Message ${filterTooStrongMessage} was not found`
    );
  });

  // reload records
  describe('reloadRecords', () => {
    it('should send command "getresults" to backend in order to request all stored records', () => {
      let expectedCommand = {
        type: 'cmd',
        command: 'getresults',
      };

      let sendArguments = [];
      let sendSpy = spyOnStoreArguments(communicationService, 'send', sendArguments);
      // call reload function
      (component as any).reloadRecords();

      expect(sendSpy).toHaveBeenCalled();
      expect(sendArguments[0].type).toEqual(expectedCommand.type);
      expect(sendArguments[0].command).toEqual(expectedCommand.command);
    });
  });
});
