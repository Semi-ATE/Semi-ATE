import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { SystemInformationComponent } from './system-information.component';
import { SystemState, Status } from 'src/app/models/status.model';
import { By } from '@angular/platform-browser';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { InformationComponent } from '../basic-ui-elements/information/information.component';
import { MockServerService } from './../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { expectWaitUntil } from './../test-stuff/auxillary-test-functions';
import { StoreModule } from '@ngrx/store';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { AppstateService } from '../services/appstate.service';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';

describe('SystemInformationComponent', () => {
  let component: SystemInformationComponent;
  let fixture: ComponentFixture<SystemInformationComponent>;
  let debugElement: DebugElement;
  let status: Status;
  let mockServerService: MockServerService;
  let expectedLabelTexts = ['System', 'Number of Sites', 'Time', 'Environment', 'Handler', 'Lot Number'];

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      providers: [],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer // key must be equal to the key define in interface AppState, i.e. userSettings
        })
      ],
      declarations: [ SystemInformationComponent, CardComponent, InformationComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);
    fixture = TestBed.createComponent(SystemInformationComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    status = {
      deviceId: 'invalid',
      env: 'invalid',
      handler: 'invalid',
      time: 'invalid',
      sites: [],
      program: 'invalid',
      log: 'invalid',
      state: SystemState.connecting,
      reason: 'invalid',
      lotNumber: '',
    };
    fixture.detectChanges();
  });

  afterAll(() => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)?.remove();
  });

  it('should create status component', () => {
    expect(component).toBeTruthy();
  });

  it('should display "System Information" as label text', () => {
    expect(component.informationCardConfiguration.labelText).toBe('System Information');
  });

  it('should show error messages when system state is ' + JSON.stringify(SystemState.error), () => {
    expect(component.showError()).toBeDefined();

    let errorMsg = 'system has error';
    let errorElement = debugElement.query(By.css('.error h3'));

    if (component.showError()) {
      status.reason = errorMsg;
      expect(errorElement.nativeElement.textContent).toBe('system has error');
    }
  });

  it('should support hr tag', () => {
    let hrElement = debugElement.nativeElement.querySelector('hr');
    expect(hrElement).toBeTruthy();
  });

  it('should contain 2 app-card tags', () => {
    let cardElement = debugElement.nativeElement.querySelectorAll('app-card');

    expect(cardElement).not.toEqual(null);
    expect(cardElement.length).toBe(2);
  });

  it('current system status is ' + JSON.stringify(SystemState.connecting), () => {
    expect(status.state).toBe('connecting');
  });

  describe('When system state is ' + JSON.stringify(SystemState.connecting), () => {
    it('should support heading', () => {
      let appCardBody = debugElement.query(By.css(('app-card app-card .card .body')));
      expect(appCardBody.nativeElement.textContent).toBe('Identifying Test System!');
    });

    it('should display labelText "System Identification"', () => {
      let appCardHeader = debugElement.query(By.css(('app-card app-card .card .header')));
      expect(appCardHeader.nativeElement.textContent).toBe('System Identification');
    });
  });

  describe('computeTextToDisplay', () => {
    it('should return default string if input is empty string', () => {
      let emptyString = '';
      let defaultString = 'default';
      expect((component as any).computeTextToDisplay(emptyString,defaultString)).toBe(defaultString);
    });
    it('should return default string if input is "null"', () => {
      let defaultString = 'default';
      expect((component as any).computeTextToDisplay(null,defaultString)).toBe(defaultString);
    });
  });

  describe('When system state is neither ' + JSON.stringify(SystemState.connecting) + ' nor ' + JSON.stringify(SystemState.error), () => {
    it('should contain information for the following topics: ' + JSON.stringify(expectedLabelTexts), async () => {

      function foundAPPInformation(): boolean {
        let element = debugElement.queryAll(By.css('app-information .information h2'));
        if (element.length === expectedLabelTexts.length) {
          return true;
        }
        return false;
      }

      // send initialized message
      mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED]);

      await expectWaitUntil(
        () => {
          fixture.detectChanges();
        },
        foundAPPInformation,
        'Did not find ' + expectedLabelTexts.length + ' app-information elements');

      let currentTopics = debugElement.queryAll(By.css('app-information .information h2'))
        .map(e => e.nativeElement.innerText);

      expect(currentTopics).toEqual(jasmine.arrayWithExactContents(expectedLabelTexts));
    });

    it('should display label texts: ' + JSON.stringify(expectedLabelTexts), async () => {
      expect(component.infoContentCardConfiguration.labelText).toEqual('');

      function foundLabeTexts(): boolean {
        let element = debugElement.queryAll(By.css('app-information'));
        return element.length === expectedLabelTexts.length;
      }
      // send initialized message
      mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED]);
      await expectWaitUntil(
        () => {
          fixture.detectChanges();
        },
        foundLabeTexts,
        'Did not find ' + expectedLabelTexts.length + ' app-information elements');

      let labelElements = [];
      debugElement.queryAll(By.css('app-information h2'))
        .forEach(a => labelElements
          .push(a.nativeElement.innerText));

      expect(labelElements).toEqual(jasmine.arrayWithExactContents(expectedLabelTexts));
    });

    it('should display value of system information', async () => {
      expect(component.systemInformationConfiguration.value).toEqual('connecting');

      function foundLabeTexts(): boolean {
        let element = debugElement.queryAll(By.css('app-information'));
        if (element.length === expectedLabelTexts.length) {
          return true;
        }
        return false;
      }
      // send testing message
      mockServerService.setUpdateTime(false);
      mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING]);

      await expectWaitUntil(
        () => {
          fixture.detectChanges();
        },
        foundLabeTexts,
        'Did not find ' + expectedLabelTexts.length + ' app-information elements'
      );

      let valueTexts = [];
      debugElement.queryAll(By.css('app-information h3'))
        .forEach(a => valueTexts
          .push(a.nativeElement.innerText));

      expect(valueTexts).toEqual([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING.payload.device_id,
        constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING.payload.systemTime,
        constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING.payload.env,
        constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING.payload.handler,
        constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING.payload.lot_number
      ]);
    });
  });
});
