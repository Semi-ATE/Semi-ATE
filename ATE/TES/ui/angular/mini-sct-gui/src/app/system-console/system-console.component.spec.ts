import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { SystemConsoleComponent } from './system-console.component';
import { ConsoleEntry } from 'src/app/models/console.model';
import { DebugElement } from '@angular/core';
import { MockServerService } from './../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from './../test-stuff/auxillary-test-functions';
import { AppstateService } from '../services/appstate.service';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';

describe('SystemConsoleComponent', () => {
  let msg: ConsoleEntry;
  let component: SystemConsoleComponent;
  let fixture: ComponentFixture<SystemConsoleComponent>;
  let debugElement: DebugElement;
  let appStateService : AppstateService;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    
    TestBed.configureTestingModule({
      declarations: [ 
        SystemConsoleComponent,
        ButtonComponent
      ],
      providers: [ 
      ],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          result: resultReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
        }),
      ],
      schemas: []}
    ).compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);

    fixture = TestBed.createComponent(SystemConsoleComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterAll( () => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)?.remove();
  });

  it('should create console component', () => {
    expect(component).toBeDefined();
  });

  it('should have "clear" button', () => {
    const buttons = debugElement.queryAll(By.css('app-button'));
    const clearButtons = buttons.filter(b => b.nativeElement.innerText.includes('Clear'));
    expect(clearButtons.length).toBe(1, 'There should be a unique button with label text "Clear"');
  });

  it('should show a table with columns "Date", "Topic" and "Description"', () => {
    const expectedTableHeaders = ['Date', 'Topic', 'Description'];
    let currentTableHeaders = [];
    const ths = debugElement.queryAll(By.css('table th'));

    ths.forEach(h => currentTableHeaders.push(h.nativeElement.innerText));
    expect(currentTableHeaders).toEqual(jasmine.arrayWithExactContents(expectedTableHeaders));
  });

  it('should show message from server', async () => {

    const expectedEntry = [
      constants.TEST_APP_MESSAGE_SITE_7_TESTING.payload.topic,
      'status: ' + constants.TEST_APP_MESSAGE_SITE_7_TESTING.payload.payload.state
    ];

    function entryFound(row: Array<string>): boolean {
      let rows = [];
      debugElement.queryAll(By.css('tr'))
        .filter(
          r => {
            let rowElements = [];
            r.queryAll(By.css('.topic, .description')).forEach(e => rowElements.push(e.nativeElement.innerText));
            rows.push(rowElements);
          }
      );

      return rows.filter( r => JSON.stringify(r) === JSON.stringify(row)).length > 0;
    }

    expect(entryFound(expectedEntry)).toBeFalsy('At the beginning there is no entry with "status, testing"');

    // mock some server message
    mockServerService.setMessages([
      constants.TEST_APP_MESSAGE_SITE_7_TESTING,
    ]);

    await expectWaitUntil(
      () => {
        fixture.detectChanges();
      },
      () => entryFound(expectedEntry),
      'No entry: "' + expectedEntry + '" has been found');
  });
});

