import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HeaderComponent } from './header.component';
import { MenuComponent } from '../../menu/menu.component';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { RouterModule } from '@angular/router';
import { Store, StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { SystemStatusComponent } from 'src/app/system-status/system-status.component';
import { DebugElement } from '@angular/core';
import { ButtonComponent } from 'src/app/basic-ui-elements/button/button.component';
import { CommunicationService } from 'src/app/services/communication.service';
import { MockServerService } from 'src/app/services/mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { expectWaitUntil, spyOnStoreArguments } from 'src/app/test-stuff/auxillary-test-functions';
import { By } from '@angular/platform-browser';
import { AppstateService } from 'src/app/services/appstate.service';
import { yieldReducer } from 'src/app/reducers/yield.reducer';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;
  let debugElement: DebugElement;
  let communicationService: CommunicationService;
  let mockServerService: MockServerService;
  let appStateService: AppstateService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HeaderComponent, MenuComponent, SystemStatusComponent, ButtonComponent ],
      imports: [
        FormsModule,
        RouterTestingModule,
        RouterModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
          yield: yieldReducer
        }),]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    communicationService = TestBed.inject(CommunicationService);
    appStateService = TestBed.inject(AppstateService);

    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create header component', () => {
    expect(component).toBeTruthy();
  });

  it(`should have as title 'MiniSCT'`, () => {
    const app = fixture.debugElement.componentInstance;
    expect(app.title).toEqual('MiniSCT');
  });
  it('should render title in a h1 tag', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('MiniSCT');
  });

  it('should contain an app-system-status tag', () => {
    let componentElement = debugElement.nativeElement.querySelectorAll('app-system-status');
    expect(componentElement).not.toEqual(null);
    expect(componentElement.length).toBe(1);
  });

  it('should contain an app-menu tag', () => {
    let componentElement = debugElement.nativeElement.querySelectorAll('app-menu');
    expect(componentElement).not.toEqual(null);
    expect(componentElement.length).toBe(1);
  });

  it('should send next command to server when button "Start DUT-Test" has been clicked', async () => {
    // generate ready for DUT Test state
    mockServerService.setRepeatMessages(false);
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_READY]);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => {
        let button = debugElement.queryAll(By.css('app-button')).find(b => b.nativeElement.innerText.includes('Start DUT-Test'));
        let buttonStyle = getComputedStyle(button.nativeElement);
        if (buttonStyle.display.includes('none'))
          return false;
        return true;
      },
      'Start DUT-Test Button did not appear'
    );

    let args = [];
    spyOnStoreArguments(communicationService, 'send', args);

    debugElement.queryAll(By.css('app-button'))
      .find(b => b.nativeElement.innerText.includes('Start DUT-Test'))
      .query(By.css('button'))
      .nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => {
        if (args?.[0].type === 'cmd' && args?.[0].command === 'next')
          return true;
        return false;
      },
      'Next command has not been send to the server'
    );
  });
  it('should send reset command to server when button "Reset System" has been clicked', async () => {
    // generate ready for DUT Test state
    mockServerService.setRepeatMessages(false);
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_SOFTERROR]);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => {
        let button = debugElement.queryAll(By.css('app-button')).find(b => b.nativeElement.innerText.includes('Reset System'));
        let buttonStyle = getComputedStyle(button.nativeElement);
        if (buttonStyle.display.includes('none'))
          return false;
        return true;
      },
      'Reset button did not appear'
    );

    let args = [];
    spyOnStoreArguments(communicationService, 'send', args);

    debugElement.queryAll(By.css('app-button'))
      .find(b => b.nativeElement.innerText.includes('Reset System'))
      .query(By.css('button'))
      .nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => {
        if (args?.[0].type === 'cmd' && args?.[0].command === 'reset')
          return true;
        return false;
      },
      'Reset command has not been send to the server'
    );
  });

});
