import { ButtonComponent } from 'src/app/basic-ui-elements/button/button.component';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { TestOptionComponent, TestOptionValue, TestOption, TestOptionLabelText } from './test-option.component';
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

describe('TestOptionComponent', () => {
  let component: TestOptionComponent;
  let fixture: ComponentFixture<TestOptionComponent>;
  let debugElement: DebugElement;

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
          result: resultReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
        })
      ],
      schemas: []
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TestOptionComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create test-option component', () => {
    expect(component).toBeTruthy();
  });

  it('should create instance of TestOptionValue', () => {
    expect(new TestOptionValue()).toBeTruthy();
  });

  it('should create instance of TestOption', () => {
    let name = 'Test Name';
    expect(new TestOption(name)).toBeTruthy();
    expect(new TestOption(name).name).toBe(name);
  });

  describe('Class TestOption', () => {
    it('should change values from onChange() when checked element is true ', () => {
      let testOption = new TestOption('Test');
      let checked = true;
      testOption.onChange(checked);

      expect(testOption.toBeAppliedValue.active).toBe(true);
      expect(testOption.inputConfig.disabled).toBe(false);
    });

    it('should get true value from haveToApply() when some change occured', () => {
      let testOption = new TestOption('Test');
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
      .filter(e => !e.classes['toggle'])
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
      let checkbox = checkboxes.filter(e => e.nativeElement.innerText === 'Stop on Fail')[0].nativeElement.querySelector('input');
      expect(checkbox.hasAttribute('disabled')).toBeTrue();
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
      let checkbox = checkboxes.filter(e => e.nativeElement.innerText === 'Stop on Fail')[0].nativeElement.querySelector('input');

      expect(checkbox.hasAttribute('disabled')).toBeFalsy();
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
  });
});
