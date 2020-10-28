import { InputComponent } from './../../basic-ui-elements/input/input.component';
import { ButtonComponent } from './../../basic-ui-elements/button/button.component';
import { CardComponent } from 'src/app/basic-ui-elements/card/card.component';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { LotHandlingComponent } from './lot-handling.component';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { SystemState } from 'src/app/models/status.model';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { CommunicationService } from 'src/app/services/communication.service';
import { MockServerService } from 'src/app/services/mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { spyOnStoreArguments } from 'src/app/test-stuff/auxillary-test-functions';

describe('LotHandlingComponent', () => {
  let component: LotHandlingComponent;
  let fixture: ComponentFixture<LotHandlingComponent>;
  let debugElement: DebugElement;
  let communicationService: CommunicationService;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LotHandlingComponent, ButtonComponent, InputComponent, CardComponent],
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
    communicationService = TestBed.inject(CommunicationService);
    fixture = TestBed.createComponent(LotHandlingComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create lot-handling component', () => {
    expect(component).toBeTruthy();
  });

  it('should have header text for card element', () => {
    const headerText = debugElement.query(By.css('app-card h2'))?.nativeElement.innerText;
    expect(headerText).toBe('Lot Handling');
  });

  it('should show an unload lot button', () => {
    const unLoadButton = debugElement.query(By.css('.unloadLotBtn app-button'));
    expect(unLoadButton.nativeElement.innerText).toBe('Unload Lot');
  });

  it('should show input field for lot number', () => {
    const input = debugElement.query(By.css('.lotInput app-input'));
    expect(input.nativeElement).toBeDefined();
  });

  it('should display error message', () => {
    const inputElement = debugElement.nativeElement.querySelector('.lotInput app-input');
    component.lotNumberInputConfig.value = '1234';
    component.loadLot();
    fixture.detectChanges();
    expect(inputElement.textContent).toBe('A lot number should be in 6.3 format like \"123456.123\"');
  });

  it('should send lot number to the server', () => {
    // we need a valid lot number, i.e. 6-point-3-format
    const lotNumber = '123456.123';
    component.lotNumberInputConfig.value = lotNumber;
    fixture.detectChanges();

    let communicationServiceRetrievedSendArgument = [];
    let sendSpy = spyOnStoreArguments(communicationService, 'send', communicationServiceRetrievedSendArgument);

    component.loadLot();
    fixture.detectChanges();
    expect(sendSpy).toHaveBeenCalled();
    expect(communicationServiceRetrievedSendArgument[0].lot_number).toEqual(lotNumber);
  });

  it('input field should be disabled in states connecting, testing, ready and unloading but enabled in state initialized', () => {
    // connecting
    (component as any).updateStatus({
      deviceId: 'MiniSCT',
      env: 'Environment',
      handler: 'Handler',
      time: '1st July 2020, 19:45:03',
      sites: ['A'],
      program: '',
      log: '',
      state: SystemState.connecting,
      reason: '',
    });
    fixture.detectChanges();

    let input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    expect(input.hasAttribute('disabled')).toBeTruthy();
    // testing
    (component as any).updateStatus({
      deviceId: 'MiniSCT',
      env: 'Environment',
      handler: 'Handler',
      time: '1st July 2020, 19:45:03',
      sites: ['A'],
      program: '',
      log: '',
      state: SystemState.testing,
      reason: '',
    });

    fixture.detectChanges();
    input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    expect(input.hasAttribute('disabled')).toBeTruthy();

    // unloading
    (component as any).updateStatus({
      deviceId: 'MiniSCT',
      env: 'Environment',
      handler: 'Handler',
      time: '1st July 2020, 19:45:03',
      sites: ['A'],
      program: '',
      log: '',
      state: SystemState.unloading,
      reason: '',
    });

    fixture.detectChanges();
    input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    expect(input.hasAttribute('disabled')).toBeTruthy();

    // ready
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

    input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    expect(input.hasAttribute('disabled')).toBeTruthy();

    // initialized
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

    input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    expect(input.hasAttribute('disabled')).toBeFalsy();
  });

  it('should call method loadLot when the enter key is pressed',() => {
    let spy = spyOn(component, 'loadLot');

    let input = fixture.debugElement.query(By.css('app-input')).nativeElement.querySelector('input');
    input.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter'}));

    expect(spy).toHaveBeenCalled();
  });

  describe('When system state is "ready"', () => {
    it('unload lot button should be active', () => {
      // ready
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
      let buttons = fixture.debugElement.queryAll(By.css('app-button'));
      let unloadLotButton = buttons.filter(e => e.nativeElement.innerText === 'Unload Lot')[0].nativeElement.querySelector('button');
      expect(unloadLotButton.hasAttribute('disabled')).toBeFalsy('unload lot button is expected to be active');
    });

    it('should call method unloadLot when button clicked',() => {

      // ready
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
      let spy = spyOn(component, 'unloadLot');
      let buttons = fixture.debugElement.queryAll(By.css('app-button'));
      let unloadLotButton = buttons.filter(e => e.nativeElement.innerText === 'Unload Lot')[0].nativeElement.querySelector('button');
      unloadLotButton.click();
      fixture.detectChanges();

      expect(spy).toHaveBeenCalled();
    });
  });
});
