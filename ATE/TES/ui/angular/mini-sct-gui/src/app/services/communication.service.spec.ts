import { TestBed } from '@angular/core/testing';
import { CommunicationService } from './communication.service';
import { MockServerService } from './mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';

describe('CommunicationService', () => {

  let service: CommunicationService;
  let mockServerService: MockServerService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [],
      imports: [],
      declarations: [],
    });
    mockServerService = TestBed.inject(MockServerService);
    service = TestBed.inject(CommunicationService);
  });

  afterAll( () => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)?.remove();
  });

  it('should create an CommunicationService instance', () => {
    expect(service).toBeTruthy();
  });

  it('should get message from observable', async () => {

    let called = false;

    // first subscribe to the service for receiving messages
    service.message.subscribe( msg => called = true);

    // mock some server message
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_READY]);

    // wait until condition (all menu items are enabled)
    let messageReceived = () => {return called;};

    await expectWaitUntil(
      () => {
      },
      messageReceived,
      'No message has been received'
    );
  });
});
