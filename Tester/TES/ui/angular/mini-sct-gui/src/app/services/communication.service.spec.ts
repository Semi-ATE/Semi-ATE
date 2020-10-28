import { TestBed } from '@angular/core/testing';
import { CommunicationService } from './communication.service';
import { MockServerService } from './mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { expectWaitUntil, spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';
import { WebsocketService } from './websocket.service';
import { connectionIdReducer, initialState } from '../reducers/connectionid.reducer';
import { StoreModule } from '@ngrx/store';

describe('CommunicationService', () => {

  let service: CommunicationService;
  let mockServerService: MockServerService;
  let webSocketService: WebsocketService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [],
      imports: [
        StoreModule.forRoot({
          connectionId: connectionIdReducer
        })
      ],
      declarations: [],
    });
    mockServerService = TestBed.inject(MockServerService);
    webSocketService = TestBed.inject(WebsocketService);
    service = TestBed.inject(CommunicationService);
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create an CommunicationService instance', () => {
    expect(service).toBeTruthy();
  });

  it('should get message from observable', async () => {
    let called = false;

    // first subscribe to the service for receiving messages
    let subscription = service.message.subscribe( msg => called = true);

    // mock some server message
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_READY]);

    await expectWaitUntil(
      null,
      () => called,
      'No message has been received'
    );

    subscription.unsubscribe();
  });

  it('should attach connection id to the send json message', () => {
    let args = [];
    spyOnStoreArguments(webSocketService, 'send', args);
    service.send({});
    expect(args[0].connectionid).toEqual(initialState);
  });
});
