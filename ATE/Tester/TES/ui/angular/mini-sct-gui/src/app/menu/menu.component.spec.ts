import { FormsModule } from '@angular/forms';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { InputComponent } from 'src/app/basic-ui-elements/input/input.component';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { TestOptionComponent } from './../system-control/test-option/test-option.component';
import { TestExecutionComponent } from './../system-control/test-execution/test-execution.component';
import { LotHandlingComponent } from './../system-control/lot-handling/lot-handling.component';
import { CardComponent } from 'src/app/basic-ui-elements/card/card.component';
import { SystemConsoleComponent } from './../system-console/system-console.component';
import { SystemControlComponent } from './../system-control/system-control.component';
import { SystemInformationComponent } from './../system-information/system-information.component';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { MenuComponent } from './menu.component';
import { RouterTestingModule } from '@angular/router/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { SystemState } from 'src/app/models/status.model';
import { MenuItem, MINISCT_ROUTES } from '../routing-table';
import { InformationComponent } from '../basic-ui-elements/information/information.component';
import { Router } from '@angular/router';
import { MockServerService } from '../services/mockserver.service';
import * as constants from './../services/mockserver-constants';
import { CommunicationService } from '../services/communication.service';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { AppstateService } from '../services/appstate.service';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { yieldReducer } from '../reducers/yield.reducer';
import { BinTableComponent } from '../bin-table/bin-table.component';
import { binReducer } from '../reducers/bintable.reducer';

describe('MenuComponent', () => {
  let component: MenuComponent;
  let fixture: ComponentFixture<MenuComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let appstateService: AppstateService;
  let router: Router;
  const expectedMenuEntries = [ 'Information', 'Bin', 'Control', 'Records', 'Logging'];

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        MenuComponent,
        SystemInformationComponent,
        SystemControlComponent,
        SystemConsoleComponent,
        CardComponent,
        InformationComponent,
        LotHandlingComponent,
        TestExecutionComponent,
        TestOptionComponent,
        ButtonComponent,
        InputComponent,
        CheckboxComponent,
        BinTableComponent
      ],
      imports: [
        RouterTestingModule.withRoutes(MINISCT_ROUTES),
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
          yield: yieldReducer,
          binTable: binReducer
        }
      )],
      providers: [
        CommunicationService,
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    appstateService = TestBed.inject(AppstateService);
    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(MenuComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    mockServerService.ngOnDestroy();
  });

  it('should create menu component', () => {
    expect(component).toBeTruthy();
  });

  it('should render the following menu items: ' + JSON.stringify(expectedMenuEntries), () => {
    let currentMenuEntries = [];
    debugElement.queryAll(By.css('a'))
      .filter(e => !e.classes.space)
      .forEach(a => currentMenuEntries
        .push(a.nativeElement.innerText));

    expect(currentMenuEntries).toEqual(jasmine.arrayWithExactContents(expectedMenuEntries));
  });

  it('should show ' + MenuItem.Info + ' page on startup', () => {
    spyOnProperty(router, 'url').and.returnValue('/' + MenuItem.Info);
    fixture.detectChanges();

    const activeMenuItems = debugElement.queryAll(By.css('.active'));
    expect(activeMenuItems.length).toEqual(1, 'there is only a single active menu item at the same time');
    expect(activeMenuItems[0].nativeElement.innerText).toEqual('Information');
  });

  it('should not show any disabled menu item when system is in state ' + SystemState.ready, async () => {
    // set system state via mockserverservice to connecting
    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_CONNECTING
    ]);

    let resultAndControlMenuItemAreDisabled = () => {
      let liList = debugElement.queryAll(By.css('li.disabled'))
        .filter(e => (e.nativeElement.innerText === 'Records' || e.nativeElement.innerText === 'Control'));
      if (liList.length === 2) {
        return true;
      }
      return false;
    };

    await expectWaitUntil(
      () => {
        fixture.detectChanges();
      },
      resultAndControlMenuItemAreDisabled,
      'Result and control menu itemms arent disabled');

    // enable all menu items by setting status to ready
    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_READY
    ]);

    // wait until condition (all menu items are enabled)
    let thereIsNoDisabledMenuItem = () => {
      let liList = debugElement.queryAll(By.css('li.disabled'));
      if (liList.length === 0) {
        return true;
      }
      return false;
    };

    await expectWaitUntil(
      () => {
        fixture.detectChanges();
      },
      thereIsNoDisabledMenuItem,
      'At least one list item is disabled',
    );
  });

  it('should call function "isActive" when menu item ' + MenuItem.Logging + ' is clicked', async () => {
    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_CONNECTING
    ]);

    let loggingIsNotDisabled = () => {
      let liList = debugElement.queryAll(By.css('li.disabled'))
        .filter(e => e.nativeElement.innerText === 'Logging');
      if (liList.length === 0) {
        return true;
      }
      return false;
    };

    await expectWaitUntil(
      () => {
        fixture.detectChanges();
      },
      loggingIsNotDisabled,
      'Logging menu item should not be disabled',
    );

    // now we can click Logging menu item
    let loggingList = debugElement.queryAll(By.css('li'))
        .filter(e => e.nativeElement.innerText === 'Logging');

    expect(loggingList.length).toEqual(1, 'Logging menu item is unique');
    // set current url to '/logging'
    spyOnProperty(router, 'url').and.returnValue('/' + MenuItem.Logging);
    // prepare test
    let isActiveSpy = spyOn(component, 'isActive').and.callThrough();

    // click logging menu item
    loggingList[0].nativeElement.click();
    let loggingIsActive = () => debugElement.queryAll(By.css('li a.active'))
      .filter(r => r.nativeElement.innerText === 'Logging').length === 1;

    // wait until all menu items are enabled
    await expectWaitUntil(
      () => fixture.detectChanges(),
      loggingIsActive,
      'Logging menu item should be active');

    expect(isActiveSpy).toHaveBeenCalled();
  });

  it('should navigate to' + MenuItem.Info + ', when system state is ' + SystemState.connecting, () => {
    // mock system status and set systemState to connecting
    (component as any).status = {
      deviceId: '',
      env: '',
      handler: '',
      time: '',
      sites: [],
      program: '',
      log: '',
      state: SystemState.connecting,
      reason: '',
      lotNumber: ''
    };
    let args = [];
    let navigateByUrlSpy = spyOnStoreArguments((component as any).router, 'navigateByUrl', args);
    spyOnProperty(router, 'url').and.returnValue('/' + MenuItem.Control);
    expect((component as any).resultsDisabled()).toEqual(true);
    (component as any).navigateToInformationIfNeeded();
    expect(navigateByUrlSpy).toHaveBeenCalled();
    expect(args[0]).toContain(MenuItem.Info);
    expect(args[1].skipLocationChange).toEqual(false, `Location must change to ${MenuItem.Info}`);
  });

  it('should navigate to' + MenuItem.Bin + ', when menu item ' + MenuItem.Bin + ' is clicked', async () => {
    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED
    ]);

    let binList = debugElement.queryAll(By.css('li'))
        .filter(e => e.nativeElement.innerText === 'Bin');

    expect(binList.length).toEqual(1, 'Bin menu item is unique');

    spyOnProperty(router, 'url').and.returnValue('/' + MenuItem.Bin);

    let isActiveSpy = spyOn(component, 'isActive').and.callThrough();
    binList[0].nativeElement.click();
    let binIsActive = () => debugElement.queryAll(By.css('li a.active'))
      .filter(r => r.nativeElement.innerText === 'Bin').length === 1;

    await expectWaitUntil(
      () => fixture.detectChanges(),
      binIsActive,
      'Bin menu item should be active');

    expect(isActiveSpy).toHaveBeenCalled();
  });
});
