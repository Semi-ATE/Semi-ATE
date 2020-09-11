import { TestBed } from '@angular/core/testing';
import { WebsocketService } from './websocket.service';
import { MockServerService } from './mockserver.service';
import * as constants from './../services/mockserver-constants';
import { spyOnStoreArguments } from '../test-stuff/auxillary-test-functions';

describe('WebsocketService', () => {
  let service: WebsocketService;
  let mockServer: MockServerService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [WebsocketService ]
    });
    mockServer = TestBed.inject(MockServerService);
    service = TestBed.inject(WebsocketService);
  });

  afterEach(() => {
    mockServer.ngOnDestroy();
  });

  it('should create a WebsocketService instance', () => {
    expect(service).toBeDefined();
  });

  describe('connect', () => {
    it('should return existing subject when called for the second time', () => {
      let resultFirst = service.connect('127.0.0.1');
      let resultSecond = service.connect('127.0.0.1');
      expect(resultFirst).toBe(resultSecond);
    });
  });

  describe('send', () => {
    it('should call next function of the websocketsubject', () => {
      service.connect('127.0.0.1');
      let nextArguments = [];
      let spySubject = spyOnStoreArguments((service as any).subject, 'next', nextArguments);
      service.send({key: 'Value'});
      expect(spySubject).toHaveBeenCalled();
      expect(nextArguments[0].key).toEqual('Value');
    });
  });
});
