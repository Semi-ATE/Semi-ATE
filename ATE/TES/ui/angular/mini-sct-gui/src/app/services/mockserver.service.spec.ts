import { TestBed } from '@angular/core/testing';
import { MockServerService } from './mockserver.service';
import * as constants from './mockserver-constants';

describe('MockServerService', () => {
  let service: MockServerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.get(MockServerService);
  });

  afterEach(() => {
     document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID).remove();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('must add element to DOM for CI build', () => {
    let mockServerElement = document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID);
    expect(mockServerElement).toBeTruthy('If the MockserverService is executed there must be a special element located in DOM.');
  });
});
