import { ButtonComponent } from 'src/app/basic-ui-elements/button/button.component';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { TestOptionComponent, TestOption, TestOptionLabelText } from './test-option.component';
import { By } from '@angular/platform-browser';
import { SystemState } from 'src/app/models/status.model';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { InputComponent } from 'src/app/basic-ui-elements/input/input.component';
import { CardComponent } from 'src/app/basic-ui-elements/card/card.component';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { CommunicationService } from 'src/app/services/communication.service';
import { TestOptionType } from 'src/app/models/usersettings.model';
import { MockServerService } from 'src/app/services/mockserver.service';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import * as constants from 'src/app/services/mockserver-constants';
import { expectWaitUntil, spyOnStoreArguments } from 'src/app/test-stuff/auxillary-test-functions';
import { AppstateService } from 'src/app/services/appstate.service';

describe('TestOptionComponent', () => {
  let component: TestOptionComponent;
  let fixture: ComponentFixture<TestOptionComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let communicationService: CommunicationService;
  let appStateService: AppstateService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        TestOptionComponent,
        ButtonComponent,
        CheckboxComponent,
        InputComponent,
        CardComponent,],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer // key must be equal to the key define in interface AppState, i.e. userSettings
        })
      ],
      schemas: []
    })
      .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    appStateService = TestBed.inject(AppstateService);
    communicationService = TestBed.inject(CommunicationService);
    fixture = TestBed.createComponent(TestOptionComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create test-option component', () => {
    expect(component).toBeTruthy();
  });

  it('should create instance of TestOption', () => {
    let type = TestOptionType.stopOnFail;
    expect(new TestOption(type)).toBeTruthy();
    expect(new TestOption(type).type).toBe(type);
  });

  describe('Class TestOption', () => {
    it('should change values from onChange() when checked element is true ', () => {
      let testOption = new TestOption(TestOptionType.stopOnFail);
      let checked = true;
      testOption.onChange(checked);

      expect(testOption.toBeAppliedValue.active).toBe(true);
      expect(testOption.inputConfig.disabled).toBe(false);
    });

    it('should get true value from haveToApply() when some change occured', () => {
      let testOption = new TestOption(TestOptionType.triggerOnFailure);
      let anyChanges = false;
      if (testOption.toBeAppliedValue.active !== testOption.currentValue.active) {
        anyChanges = true;
      }

      expect(testOption.haveToApply()).toEqual(anyChanges);
    });

  });

  it('should show apply- and reset-button', () => {
    let buttonLabels = debugElement.queryAll(By.css('button')).map(b => b.nativeElement.innerText);
    expect(buttonLabels).toEqual(jasmine.arrayWithExactContents([TestOptionLabelText.apply, TestOptionLabelText.reset]));
  });

  it('should show the test options stored in array testOptions', () => {
    let checkboxLabels = debugElement
      .queryAll(By.css('app-checkbox label'))
      .filter(e => !e.classes.toggle)
      .map(e => e.nativeElement.innerText);
    expect(checkboxLabels).toEqual(jasmine.arrayWithExactContents(((component as any).testOptions as TestOption[]).map(o => o.checkboxConfig.labelText)));
  });

  it('should call method resetTestOptions when reset button clicked', () => {

    // update the status of this component
    (component as any).updateStatus({
      deviceId: 'MiniSCT',
      env: 'Environment',
      handler: 'Handler',
      time: '1st July 2020, 19:45:03',
      sites: ['A'],
      program: '',
      log: '',
      state: SystemState.ready,
      reason: '',
    });

    fixture.detectChanges();
    let checkboxes = fixture.debugElement.queryAll(By.css('app-checkbox'));
    let checkbox = checkboxes.filter(e => e.nativeElement.innerText === 'Stop on Fail')[0].nativeElement.querySelector('.slider');

    checkbox.click();
    fixture.detectChanges();

    let buttons = fixture.debugElement.queryAll(By.css('app-button'));
    let resetButton = buttons.filter(e => e.nativeElement.innerText === 'Reset')[0].nativeElement.querySelector('button');

    let spy = spyOn(component, 'resetTestOptions');
    resetButton.click();
    fixture.detectChanges();

    expect(spy).toHaveBeenCalled();
  });

  it('should update test options when received user settings from server', async () => {

    function checkTestOption(testOption: TestOption, active: boolean, value?: number): boolean {
      if( testOption.checkboxConfig.checked === active ) {
        if (testOption.currentValue.active === active) {
          if (value || value > 0) {
            if (testOption.currentValue.value === value) {
              if (testOption.inputConfig.value === value.toString()) {
                return true;
              }
            }
          } else {
            return true;
          }
        }
      }
      return false;
    }

    const settingsFromServer = {
      type: 'usersettings',
      payload: {
        testoptions: [
          {
            name: TestOptionType.stopOnFail,
            active: true,
            value: -1,
          },
          {
            name: TestOptionType.stopAtTestNumber,
            active: false,
            value: 4
          },
          {
            name: TestOptionType.triggerSiteSpecific,
            active: true,
            value: -1
          },
        ]
      }
    };

    mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        settingsFromServer
      ]
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => {
        if (checkTestOption(component.stopAtTestNumberOption, false, 4)) {
          if (checkTestOption(component.stopOnFailOption, true)) {
            if (checkTestOption(component.triggerSiteSpecificOption, true)) {
              return true;
            }
          }
        }
        return false;
      },
      'Expected test option settings did not load',
      200,
      3000
    );
  });

  describe('Option: Stop-On-Fail', () => {

    it('should display "Stop on Fail"', () => {
      expect(component.stopOnFailOption.checkboxConfig.labelText).toContain('Stop on Fail');
    });

    it('should be disabled when system is initialized', () => {
      // update the status of this component
      (component as any).updateStatus({
        deviceId: 'MiniSCT',
        env: 'Environment',
        handler: 'Handler',
        time: '1st July 2020, 19:45:03',
        sites: ['A'],
        program: '',
        log: '',
        state: SystemState.initialized,
        reason: '',
      });
      fixture.detectChanges();
      let checkboxes = fixture.debugElement.queryAll(By.css('app-checkbox'));
      let checkbox = checkboxes.find(e => e.nativeElement.innerText === 'Stop on Fail');
      expect(checkbox.query(By.css('.disabled'))).toBeDefined();
    });

    it('should be active when system state is ready', () => {

      // update the status of this component
      (component as any).updateStatus({
        deviceId: 'MiniSCT',
        env: 'Environment',
        handler: 'Handler',
        time: '1st July 2020, 19:45:03',
        sites: ['A'],
        program: 'Loaded Program Name',
        log: '',
        state: SystemState.ready,
        reason: '',
      });
      fixture.detectChanges();

      let checkboxes = fixture.debugElement.queryAll(By.css('app-checkbox'));
      let checkbox = checkboxes.find(e => e.nativeElement.innerText === 'Stop on Fail');
      expect(checkbox.query(By.css('.disabled'))).toBeNull();
    });

    it('should call sendOptionsToServer method when apply button clicked', () => {
      // update the status of this component
      (component as any).updateStatus({
        deviceId: 'MiniSCT',
        env: 'Environment',
        handler: 'Handler',
        time: '1st July 2020, 19:45:03',
        sites: ['A'],
        program: '',
        log: '',
        state: SystemState.ready,
        reason: '',
      });
      fixture.detectChanges();

      let checkboxes = fixture.debugElement.queryAll(By.css('app-checkbox'));
      let checkbox = checkboxes.filter(e => e.nativeElement.innerText === 'Stop on Fail')[0].nativeElement.querySelector('.slider');

      checkbox.click();
      fixture.detectChanges();

      let buttons = fixture.debugElement.queryAll(By.css('app-button'));
      let applyButton = buttons.filter(e => e.nativeElement.innerText === 'Apply')[0].nativeElement.querySelector('button');

      let spy = spyOn(component, 'sendOptionsToServer');
      applyButton.click();

      fixture.detectChanges();
      expect(spy).toHaveBeenCalled();
    });

    it('should pass send options to the send function of the communication service', () => {
      // update the status of this component
      (component as any).updateStatus({
        deviceId: 'MiniSCT',
        env: 'Environment',
        handler: 'Handler',
        time: '1st July 2020, 19:45:03',
        sites: ['A'],
        program: '',
        log: '',
        state: SystemState.ready,
        reason: '',
      });
      fixture.detectChanges();

      // configure stop on fail option
      let checkboxes = fixture.debugElement.queryAll(By.css('app-checkbox'));
      let checkbox = checkboxes.filter(e => e.nativeElement.innerText === 'Stop on Fail')[0].nativeElement.querySelector('.slider');
      checkbox.click();
      fixture.detectChanges();

      // spy on send function of the communication service
      // and store received arguments to check them later
      let communicationServiceRetrievedSendArgument = [];
      let sendSpy = spyOnStoreArguments(communicationService, 'send', communicationServiceRetrievedSendArgument);

      // apply changes
      let buttons = fixture.debugElement.queryAll(By.css('app-button'));
      let applyButton = buttons.filter(e => e.nativeElement.innerText === 'Apply')[0].nativeElement.querySelector('button');
      applyButton.click();
      fixture.detectChanges();

      // check that the send function has been called
      expect(sendSpy).toHaveBeenCalled();

      // check the data that would be send to the server
      expect(communicationServiceRetrievedSendArgument[0].command).toEqual('usersettings');
      expect(communicationServiceRetrievedSendArgument[0].payload.length).toEqual(Object.keys(TestOptionType).length);
      expect(communicationServiceRetrievedSendArgument[0].payload.some(e => e.name === TestOptionType.stopOnFail)).toBeTrue();
      expect(communicationServiceRetrievedSendArgument[0]
        .payload.filter(
          e => e.name === TestOptionType.stopOnFail)[0].active).toBeTrue();
    });
  });
});
