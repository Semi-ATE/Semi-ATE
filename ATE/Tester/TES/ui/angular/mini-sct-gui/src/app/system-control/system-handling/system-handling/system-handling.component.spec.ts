import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { LogLevel } from 'src/app/models/usersettings.model';
import { AppstateService, MessageTypes } from 'src/app/services/appstate.service';
import { CommunicationService } from 'src/app/services/communication.service';
import { MockServerService } from 'src/app/services/mockserver.service';
import { expectWaitUntil, spyOnStoreArguments } from 'src/app/test-stuff/auxillary-test-functions';
import { SystemHandlingComponent } from './system-handling.component';
import { By } from '@angular/platform-browser';
import { StoreModule } from '@ngrx/store';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { yieldReducer } from 'src/app/reducers/yield.reducer';
import { CardComponent } from 'src/app/basic-ui-elements/card/card.component';
import { DropdownComponent } from 'src/app/basic-ui-elements/dropdown/dropdown.component';

describe('SystemHandlingComponent', () => {
  let component: SystemHandlingComponent;
  let fixture: ComponentFixture<SystemHandlingComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let communicationService: CommunicationService;
  let appStateService: AppstateService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        DropdownComponent,
        CardComponent,
        SystemHandlingComponent
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
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    communicationService = TestBed.inject(CommunicationService);
    appStateService = TestBed.inject(AppstateService);
    fixture = TestBed.createComponent(SystemHandlingComponent);
    debugElement = fixture.debugElement;
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
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
      'Dropdown element for setting the loglevel did not update selected index. It should be: ' + expectedSelectedIndex
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
