import { FormsModule } from '@angular/forms';
import { CheckboxComponent } from 'src/app/basic-ui-elements/checkbox/checkbox.component';
import { InputComponent } from 'src/app/basic-ui-elements/input/input.component';
import { ButtonComponent } from './../basic-ui-elements/button/button.component';
import { TestOptionComponent } from './../system-control/test-option/test-option.component';
import { TestExecutionComponent } from './../system-control/test-execution/test-execution.component';
import { LotHandlingComponent } from './../system-control/lot-handling/lot-handling.component';
import { CardComponent } from 'src/app/basic-ui-elements/card/card.component';
import { SystemSiteComponent } from './../system-site/system-site.component';
import { SystemConsoleComponent } from './../system-console/system-console.component';
import { SystemControlComponent } from './../system-control/system-control.component';
import { SystemInformationComponent } from './../system-information/system-information.component';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { MenuComponent } from './menu.component';
import { RouterTestingModule } from '@angular/router/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { SystemState } from 'src/app/models/status.model';
import { MenuItem, routes } from '../app-routing.module';
import { InformationComponent } from '../basic-ui-elements/information/information.component';
import { Router } from '@angular/router';
import { MockServerService } from '../services/mockserver.service';
import * as constants from './../services/mockserver-constants';
import { CommunicationService } from '../services/communication.service';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';

describe('MenuComponent', () => {
  let component: MenuComponent;
  let fixture: ComponentFixture<MenuComponent>;
  let debugElement: DebugElement;
  let router: Router;
  let mockServerService: MockServerService;
  const expectedMenuEntries = [ 'Information', 'Control', 'Results', 'Logging'];

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        MenuComponent,
        SystemInformationComponent,
        SystemControlComponent,
        SystemConsoleComponent,
        SystemSiteComponent,
        CardComponent,
        InformationComponent,
        LotHandlingComponent,
        TestExecutionComponent,
        TestOptionComponent,
        ButtonComponent,
        InputComponent,
        CheckboxComponent
      ],
      imports: [
        RouterTestingModule.withRoutes(routes),
        FormsModule
      ],
      providers: [
        CommunicationService,
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = new MockServerService();
    fixture = TestBed.createComponent(MenuComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    router = TestBed.get(Router);
    fixture.detectChanges();
  });

  afterEach(() => {
    fixture.destroy();
    component = null;
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID).remove();
  });

  it('should create menu component', () => {
    expect(component).toBeTruthy();
  });

  it('should render the following menu items: ' + JSON.stringify(expectedMenuEntries), () => {
    let currentMenuEntries = [];
    debugElement.queryAll(By.css('a'))
      .forEach(a => currentMenuEntries
        .push(a.nativeElement.innerText));

    expect(currentMenuEntries).toEqual(jasmine.arrayWithExactContents(expectedMenuEntries));
  });

  it('should show ' + MenuItem.Info + ' page on startup', () => {
    spyOnProperty(router, 'url', 'get').and.returnValue('/information');
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
        .filter(e => (e.nativeElement.innerText === 'Results' || e.nativeElement.innerText === 'Control'));
      if (liList.length === 2) {
        return true;
      }
      return false;
    };

    await expectWaitUntil(
      () => {
        component.ngOnInit();
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
        component.ngOnInit();
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
        component.ngOnInit();
        fixture.detectChanges();
      },
      loggingIsNotDisabled,
      'Logging menu item should not be disabled',
    );

    // now we can click Logging menu item
    let loggingList = debugElement.queryAll(By.css('li'))
        .filter(e => e.nativeElement.innerText === 'Logging');

    expect(loggingList.length).toEqual(1, 'Logging menu item is unique');

    // prepare test
    let spy = spyOnProperty(router, 'url').and.returnValue('/logging');

    let isActiveSpy = spyOn(component, 'isActive').and.callThrough();

    // click logging menu item
    loggingList[0].nativeElement.click();
    let loggingIsActive = () => debugElement.queryAll(By.css('li a.active'))
      .filter(r => r.nativeElement.innerText === 'Logging').length === 1;

    // wait until all menu items are enabled
    await expectWaitUntil(
      () => {
        component.ngOnInit();
        fixture.detectChanges();
      },
      loggingIsActive,
      'Logging menu item should be active');

    expect(spy).toBeTruthy();
    expect(isActiveSpy).toHaveBeenCalled();
  });
});
