import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { SystemConsoleComponent } from './system-console.component';
import { ConsoleEntry } from 'src/app/models/console.model';
import { DebugElement } from '@angular/core';
import { MockServerService } from './../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { By } from '@angular/platform-browser';
import { AppstateService, MessageTypes } from '../services/appstate.service';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { DropdownComponent } from '../basic-ui-elements/dropdown/dropdown.component';
import { LogLevel } from '../models/usersettings.model';
import { CommunicationService } from '../services/communication.service';
import { AppState } from '../app.state';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { yieldReducer } from '../reducers/yield.reducer';

describe('SystemConsoleComponent', () => {
  let msg: ConsoleEntry;
  let component: SystemConsoleComponent;
  let fixture: ComponentFixture<SystemConsoleComponent>;
  let debugElement: DebugElement;
  let appStateService: AppstateService;
  let mockServerService: MockServerService;
  let communicationService: CommunicationService;

  beforeEach(async(() => {

    TestBed.configureTestingModule({
      declarations: [
        SystemConsoleComponent,
        ButtonComponent,
        DropdownComponent,
        CardComponent,
      ],
      providers: [
      ],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
          yield: yieldReducer
        }),
      ],
      schemas: []}
    ).compileComponents();
  }));

  beforeEach(() => {
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
  });

  it('should have "save" button', () => {
    const buttons = debugElement.queryAll(By.css('app-button'));
    const saveButtons = buttons.filter(b => b.nativeElement.innerText.includes('Save'));
    expect(saveButtons.length).toBe(1, 'There should be a unique button with label text "Save"');
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

  it('should update log level setting accroding to server message', async () => {
    let msgFromServer = {
      type: MessageTypes.Usersettings,
      payload: {
        loglevel: LogLevel.Debug
      }
    };
    mockServerService.setMessages([msgFromServer]);
    let expectedSelectedIndex = component.setLogLevelDropdownConfig.items.findIndex(e => e.value === msgFromServer.payload.loglevel);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => component.setLogLevelDropdownConfig.selectedIndex === expectedSelectedIndex,
      'Dropdown element for setting the loglevel did not update selected idex. It should be: ' + expectedSelectedIndex
    );

    msgFromServer.payload.loglevel = LogLevel.Error;
    mockServerService.setMessages([msgFromServer]);
    expectedSelectedIndex = component.setLogLevelDropdownConfig.items.findIndex(e => e.value === msgFromServer.payload.loglevel);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => component.setLogLevelDropdownConfig.selectedIndex === expectedSelectedIndex,
      'Dropdown element for setting the loglevel did not update selected idex. It should be: ' + expectedSelectedIndex
    );
  });

  it('should send new loglevel to the server', async () => {
    let args = [];
    let spy = spyOnStoreArguments(communicationService, 'send', args);

    debugElement.query(By.css('app-dropdown li.selected')).nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.closed')) === null,
      'Dropdown did not open');


     debugElement.queryAll(By.css('app-dropdown li'))
      .find(e => e.nativeElement.innerText.includes('Error'))
      .nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => args.some(e => e.type === 'cmd' && e.command === 'setloglevel' && e.level === LogLevel.Error),
      'Command setloglevel was not send to server.');
  });
});

