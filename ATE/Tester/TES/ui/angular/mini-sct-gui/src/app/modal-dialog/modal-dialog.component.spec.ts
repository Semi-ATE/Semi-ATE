import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { StoreModule } from '@ngrx/store';
import { Router } from '@angular/router';
import { ButtonComponent } from '../basic-ui-elements/button/button.component';
import { consoleReducer } from '../reducers/console.reducer';
import { MenuItem, MINISCT_ROUTES } from '../routing-table';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { ModalDialogComponent } from './modal-dialog.component';
import { AppstateService } from '../services/appstate.service';
import { CommunicationService } from '../services/communication.service';
import { WebsocketService } from '../services/websocket.service';
import { ConsoleEntry } from '../models/console.model';
import * as constants from 'src/app/services/mockserver-constants';
import { MockServerService } from '../services/mockserver.service';

describe('ModalDialogComponent', () => {
  let component: ModalDialogComponent;
  let fixture: ComponentFixture<ModalDialogComponent>;
  let router: Router;
  let appStateService: AppstateService;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        ModalDialogComponent,
        ButtonComponent
      ],
      imports: [
        RouterTestingModule.withRoutes(MINISCT_ROUTES),
        StoreModule.forRoot({
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
        }),
      ],
      providers: [
        WebsocketService,
        CommunicationService,
        AppstateService
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(WebsocketService);
    fixture = TestBed.createComponent(ModalDialogComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    appStateService = TestBed.inject(AppstateService);
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should contain a "Close" button', () => {
    expect(component.closeButton.labelText).toEqual('Close');
  });

  it('should contain a "Show Log" button', () => {
    expect(component.navigateButton.labelText).toEqual('Show Log');
  });

  it('should be hidden on startup', () => {
    expect(component.dialogVisible).toEqual(false);
  });

  it('should close dialog message and navigate to log messages in case "Show Log" button is clicked', () => {
    const closeDialogSpy = spyOn(component, 'closeDialog');

    let args = [];
    let navigateByUrlSpy = spyOnStoreArguments((component as any).router, 'navigateByUrl', args);
    component.navigateToLogdata();
    fixture.detectChanges();
    expect(closeDialogSpy).toHaveBeenCalled();
    expect(navigateByUrlSpy).toHaveBeenCalled();
    expect(args[0]).toEqual(`/${MenuItem.Logging}`);
  });

  it('should call function "waitForMessage" in case that the App-State-Service triggers "showModalDialogEvent"', () => {
      const waitForMessageSpy = spyOn<any>(component, 'waitForMessage');
      appStateService.showModalDialog$.next();
      fixture.detectChanges();
      expect(waitForMessageSpy).toHaveBeenCalled();
  });

  it('should hide dialog in case function "closeDialog" is called', () => {
    component.dialogVisible = true;
    component.closeDialog();
    expect(component.dialogVisible).toEqual(false);
  });

  it('should show the dialog in case function "showMessage" is called', () => {
    const message: ConsoleEntry = {
      date: '07/09/2020 03:30:50 PM',
      type: 'WARNING',
      description: 'Control 0 lost',
      source: 'control 0',
      orderMessageId: 1
    };
    component.dialogVisible = false;
    (component as any).showMessage(message);

    expect(component.dialogVisible).toEqual(true);
    expect(component.dialogHeaderText).toContain(message.type);
    expect(component.dialogBodyText).toEqual(message.description);
  });

  it('should tag error messages', () => {
    const error: ConsoleEntry = {
      date: '07/09/2020 03:30:50 PM',
      type: 'ERROR',
      description: 'Control 0 lost',
      source: 'control 0',
      orderMessageId: 1
    };
    component.error = false;
    (component as any).showMessage(error);
    expect(component.error).toEqual(true);
  });

  it('should show desired message, i.e. message with expected ID', () => {
    // prepare test
    (component as any).messageOrderIdToShow = 1;
    const message: ConsoleEntry = {
      date: '07/09/2020 03:30:50 PM',
      type: 'MESSAGE',
      description: 'MESSAGE',
      source: 'control 0',
      orderMessageId: (component as any).messageOrderIdToShow
    };
    const showMessageSpy = spyOn<any>(component, 'showMessage');

    (component as any).checkMessages([message]);
    expect(showMessageSpy).toHaveBeenCalledTimes(1);

    // set ID of message to something different
    message.orderMessageId = 10;

    (component as any).checkMessages([message]);
    expect(showMessageSpy).toHaveBeenCalledTimes(1);

  });

  describe('waitForMessage', () => {
    it('should update field "messageOrderIdToShow"', () => {
      // prepare test
      (component as any).messageOrderIdToShow = 8;
      (component as any).waitForMessage(123);
      expect((component as any).messageOrderIdToShow).toEqual(123);
    });

    it('should delegate to function "checkMessages" if new console entries arrive', async () => {
      mockServerService.setRepeatMessages(false);
      mockServerService.clearMessages();
      mockServerService.setSendMessageInterval(250);

      let args = [];
      spyOnStoreArguments(component, 'checkMessages', args);

      (component as any).waitForMessage(123);

      // send some mock data, i.e. console entries
      mockServerService.setMessages([constants.LOG_ENTRIES]);

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => args[0]?.length === constants.LOG_ENTRIES.payload.length,
        'Function checkMessages has not been called'
      );

      expect(args[0].length).toEqual(constants.LOG_ENTRIES.payload.length);

      // check field description
      for ( let idx = 0; idx < args[0].length; ++idx ) {
        expect(args[0][idx].description).toEqual(constants.LOG_ENTRIES.payload[idx].description);
      }
    });
  });
});
