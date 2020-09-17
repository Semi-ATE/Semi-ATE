import { TestBed } from '@angular/core/testing';
import { MockServerService } from './mockserver.service';
import * as constants from './mockserver-constants';

describe('MockServerService', () => {
  let service: MockServerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MockServerService);
  });

  afterEach(() => {
    service.ngOnDestroy();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('must add element to DOM for CI build', () => {
    let mockServerElement = document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID);
    expect(mockServerElement).toBeTruthy('If the MockserverService is executed there must be a special element located in DOM.');
  });

  describe('appendMessage', () => {
    it('should add parameter to the end of the message array', () => {
      let msg = {
        hallo: 'test'
      };
      service.appendMessage(msg);

      expect((service as any).msgs[(service as any).msgs.length - 1]).toEqual(msg);
    });
  });
  describe('clearMessages', () => {
    it('should clear the message array', () => {
      let msg = {
        hallo: 'test'
      };
      service.appendMessage(msg);
      expect((service as any).msgs.length).toEqual(1);
      service.clearMessages();
      expect((service as any).msgs.length).toEqual(0);
    });
  });
});
