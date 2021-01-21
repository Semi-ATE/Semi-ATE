import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { SystemControlComponent } from './system-control.component';
import { InputComponent } from './../basic-ui-elements/input/input.component';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { CardComponent } from './../basic-ui-elements/card/card.component';
import { TestExecutionComponent } from './test-execution/test-execution.component';
import { TestOptionComponent } from './test-option/test-option.component';
import { LotHandlingComponent } from './lot-handling/lot-handling.component';
import { CheckboxComponent } from '../basic-ui-elements/checkbox/checkbox.component';
import { By } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { SystemHandlingComponent } from './system-handling/system-handling/system-handling.component';
import { DropdownComponent } from '../basic-ui-elements/dropdown/dropdown.component';
import { MockServerService } from '../services/mockserver.service';

describe('SystemControlComponent', () => {
  let component: SystemControlComponent;
  let fixture: ComponentFixture<SystemControlComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        SystemControlComponent,
        TestExecutionComponent,
        TestOptionComponent,
        LotHandlingComponent,
        SystemHandlingComponent,
        CardComponent,
        InputComponent,
        ButtonComponent,
        CheckboxComponent,
        DropdownComponent
      ],
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

  beforeEach( () => {
    mockServerService = TestBed.inject(MockServerService);
    fixture = TestBed.createComponent(SystemControlComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create system control component', () => {
    expect(component).toBeDefined();
  });

  it('should support labelText', () => {

    // check app-card header text
    let expectedHeaderText = 'Control';
    let appCardHeader = debugElement.nativeElement.querySelector('app-card .header');
    expect(expectedHeaderText).toEqual(component.systemControlCardConfiguration.labelText);
    expect(appCardHeader.textContent).toContain(expectedHeaderText);

    // check option label text
    let optionDebugElement = debugElement.query(By.directive(TestOptionComponent));
    let expectedOptionsLabelText = 'Options';
    let optionsAppCardHeader = debugElement.nativeElement.querySelector('#option app-card .header');
    expect(expectedOptionsLabelText).toEqual(optionDebugElement.context.testOptionCardConfiguration.labelText);
    expect(optionsAppCardHeader.textContent).toContain(expectedOptionsLabelText);
  });

  describe('Tags of the other component type', () => {
    it('should contain an app-card tag', () => {
      let componentElement = debugElement.nativeElement.querySelector('app-card');
      expect(componentElement).not.toEqual(null);
    });

    it('should contain an app-lot-handling tag', () => {
      let componentElement = debugElement.nativeElement.querySelector('app-lot-handling');
      expect(componentElement).not.toEqual(null);
    });

    it('should not contain an app-test-execution tag', () => {
      let componentElement = debugElement.nativeElement.querySelector('app-test-execution');
      expect(componentElement).toEqual(null);
    });

    it('should contain an app-test-option tag', () => {
      let componentElement = debugElement.nativeElement.querySelector('app-test-option');
      expect(componentElement).not.toEqual(null);
    });
  });
});
