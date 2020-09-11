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
});
