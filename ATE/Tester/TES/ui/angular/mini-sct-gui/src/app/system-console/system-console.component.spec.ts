import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { LogLevelString, SystemConsoleComponent } from './system-console.component';
import { DebugElement } from '@angular/core';
import { MockServerService } from './../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { By } from '@angular/platform-browser';
import { AppstateService } from '../services/appstate.service';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { CommunicationService } from '../services/communication.service';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { MultichoiceComponent } from '../basic-ui-elements/multichoice/multichoice.component';
import { InputComponent } from '../basic-ui-elements/input/input.component';
import { FormsModule } from '@angular/forms';
import { LogLevelFilterSetting, SourceFilterSetting } from '../models/storage.model';
import { StorageMap } from '@ngx-pwa/local-storage';

describe('SystemConsoleComponent', () => {
  let component: SystemConsoleComponent;
  let fixture: ComponentFixture<SystemConsoleComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let communicationService: CommunicationService;
  let storage: StorageMap;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        SystemConsoleComponent,
        ButtonComponent,
        MultichoiceComponent,
        CardComponent,
        InputComponent
      ],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
        }),
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    storage = TestBed.inject(StorageMap);
    mockServerService = TestBed.inject(MockServerService);
    communicationService = TestBed.inject(CommunicationService);
    TestBed.inject(AppstateService);
    fixture = TestBed.createComponent(SystemConsoleComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create console component', () => {
    expect(component).toBeDefined();
  });

  describe('Clear Button', () => {
    it('should be displayed', () => {
      const buttons = debugElement.queryAll(By.css('app-button'));
      const clearButtons = buttons.filter(b => b.nativeElement.innerText.includes('Clear'));
      expect(clearButtons.length).toBe(1, 'There should be a unique button with label text "Clear"');
    });

    it('should clear all messagess if it has been clicked', async () => {
      const msgFromServer = constants.LOG_ENTRIES;
      const expectedEntry = [
        msgFromServer.payload[0].date,
        msgFromServer.payload[0].type,
        msgFromServer.payload[0].description,
      ];

      function entryFound(row: Array<string>): boolean {
        let rows = [];
        debugElement.queryAll(By.css('tbody tr'))
          .forEach( r => {
              let rowElements = [];
              r.queryAll(By.css('.time, .type, .info')).forEach(e => rowElements.push(e.nativeElement.innerText));
              rows.push(rowElements);
            }
          );
        return rows.some( r => expectedEntry.every( e => r.some( a => a === e) ));
      }

      expect(entryFound(expectedEntry)).toBeFalsy('At the beginning there is no entry with "status, testing"');

      // mock some server message
      mockServerService.setMessages([
        msgFromServer
      ]);

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => entryFound(expectedEntry),
        'No entry: "' + '" has been found');

      // call clear function
      component.clearConsole();
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => !entryFound(expectedEntry),
        'Console entries still show some log entry');
    });
  });

  describe('Reload Button', () => {
    it('should be displayed', () => {
      const buttons = debugElement.queryAll(By.css('app-button'));
      const reloadButtons = buttons.filter(b => b.nativeElement.innerText.includes('Reload'));
      expect(reloadButtons.length).toBe(1, 'There should be a unique button with label text "Reload"');
    });

    it('should send command "getlogs" to server when reloadLogs method have been called', () => {
      const communicationServiceRetrievedSendArgument = [];
      const sendSpy = spyOnStoreArguments(communicationService, 'send', communicationServiceRetrievedSendArgument);

      component.reloadLogs();
      fixture.detectChanges();
      expect(sendSpy).toHaveBeenCalled();
      expect(communicationServiceRetrievedSendArgument[0].command).toEqual('getlogs');
    });
  });

  describe('Save Button', () => {
    it('should be displayed', () => {
      const buttons = debugElement.queryAll(By.css('app-button'));
      const saveButtons = buttons.filter(b => b.nativeElement.innerText.includes('Save'));
      expect(saveButtons.length).toBe(1, 'There should be a unique button with label text "Save"');
    });

    it('should send command "getlogfile" to server when getLogFile method have been called', () => {
      const communicationServiceRetrievedSendArgument = [];
      const sendSpy = spyOnStoreArguments(communicationService, 'send', communicationServiceRetrievedSendArgument);

      component.getLogFile();
      fixture.detectChanges();
      expect(sendSpy).toHaveBeenCalled();
      expect(communicationServiceRetrievedSendArgument[0].command).toEqual('getlogfile');
    });
  });

  describe('Loglevel Filter', () => {
    it('should show a multichoice field', () => {
      const multichoice = debugElement.queryAll(By.css('app-multichoice'));
      expect(multichoice.length).toBe(1, 'There should be an unique multichoice filed');
    });

    it('should show label text', () => {
      expect(component.setLogLevelFilterConfig.label).toEqual('Loglevel Filter', 'Expected label text should be "Loglevel Filter"');
    });

    it('should show expected loglevel filter items', () => {
      const expectedLogLevelFilterItems = ['Debug', 'Info', 'Warning', 'Error'];
      expect(component.setLogLevelFilterConfig.items.map(e => e.label)).toEqual(expectedLogLevelFilterItems, `Loglevel filter items should be ${expectedLogLevelFilterItems}`);
    });
  });

  it('should show an input field', () => {
    const input = debugElement.queryAll(By.css('app-input'));
    expect(input.length).toBe(1, 'There should be an unique input filed');
  });

  it('should show a table with columns "Date and Time", "Type" and "Description"', () => {
    const expectedTableHeaders = ['Date and Time', 'Type', 'Source', 'Description'];
    let currentTableHeaders = [];
    const ths = debugElement.queryAll(By.css('table th'));

    ths.forEach(h => currentTableHeaders.push(h.nativeElement.innerText));
    expect(currentTableHeaders).toEqual(jasmine.arrayWithExactContents(expectedTableHeaders));
  });

  it('should show message from server', async () => {
    const msgFromServer = constants.LOG_ENTRIES;

    const expectedEntry = [
      msgFromServer.payload[0].date,
      msgFromServer.payload[0].type,
      msgFromServer.payload[0].description,
    ];

    function entryFound(row: Array<string>): boolean {
      let rows = [];
      debugElement.queryAll(By.css('tbody tr'))
        .forEach( r => {
            let rowElements = [];
            r.queryAll(By.css('.time, .type, .info')).forEach(e => rowElements.push(e.nativeElement.innerText));
            rows.push(rowElements);
          }
        );
      return rows.some( r => expectedEntry.every( e => r.some( a => a === e) ));
    }

    expect(entryFound(expectedEntry)).toBeFalsy('At the beginning there is no entry with "status, testing"');

    // mock some server message
    mockServerService.setMessages([
      msgFromServer
    ]);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => entryFound(expectedEntry),
      'No entry: "' + '" has been found',
      200,3000);
  });

  it('should display log entries based on loglevel and source filter', () => {
    const expectedConsoleEntries = [
      {
        date: '12/03/2021 03:30:50 PM',
        type: 'DEBUG',
        description: 'testprogram',
        source: 'testapp',
        orderMessageId: 0
      },
      {
        date: '12/03/2021 03:30:50 PM',
        type: 'INFO',
        description: 'Information',
        source: 'Infomation of program',
        orderMessageId: 1
      },
      {
        date: '12/03/2021 03:30:50 PM',
        type: 'DEBUG',
        description: 'testprogram1',
        source: 'testapp1',
        orderMessageId: 2
      },
    ];

    (component as any).newConsoleEntries(expectedConsoleEntries);
    fixture.detectChanges();

    expect(component.setLogLevelFilterConfig.items.filter(e => e.checked)).toBeTruthy();
    expect(component.filteredEntries.length).toBe(3);

    component.setLogLevelFilterConfig.items[1].checked = false;
    component.sourceFilterInputConfig.value = 'test';
    component.setLogLevelFilter();
    component.sourceFilterChanged();
    fixture.detectChanges();

    expect(component.filteredEntries.length).toEqual(2);
  });

  describe('restoreSettings', () => {
    async function waitProperLoglevelFilterInitialization() {
      const expectedLabelText = 'Loglevel Filter';
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => debugElement.queryAll(By.css('label')).some(e => e.nativeElement.innerText === expectedLabelText),
        `Expected label text ${expectedLabelText} was not found.`
      );
    }

    describe('Loglevel filter', () => {
      it('should deactivate Loglevel filter', async (done) => {
        await waitProperLoglevelFilterInitialization();

        component.setLogLevelFilterConfig.items[0].checked = false;
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => !component.setLogLevelFilterConfig.items[0].checked,
          'Restore settings did not deactivate Loglevel filter');
        done();
        });
      });

      it('should apply loglevel and source filter settings from storage', async () => {
        await waitProperLoglevelFilterInitialization();

        const logLevelFilterSettings: LogLevelFilterSetting = {
          logLevelFilter: [LogLevelString.Debug]
        };

        await storage.set((component as any).getStorageKey(), logLevelFilterSettings).toPromise();

        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => component.setLogLevelFilterConfig.items[0].checked &&
                component.setLogLevelFilterConfig.items[0].label === 'Debug',
          'Restore settings did not apply loglevel filter settings from storage');
      });
    });

    async function waitUnitlSourceFilterIsInitialized() {
      const expectedLabelText = 'Source Filter';
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => debugElement.queryAll(By.css('label')).some(e => e.nativeElement.innerText === expectedLabelText),
        `Expected label text ${expectedLabelText} was not found.`
      );
    }

    describe('Source filter', () => {
      it('should apply source filter settings from storage', async () => {
        await waitUnitlSourceFilterIsInitialized();

        const sourceFilterSettings: SourceFilterSetting = {
          sourceFilter: 'test'
        };

        await storage.set((component as any).getSourceStorageKey(), sourceFilterSettings).toPromise();

        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => component.sourceFilterInputConfig.value === sourceFilterSettings.sourceFilter,
          'Restore settings did not apply source filter settings from storage');
      });
    });
  });

