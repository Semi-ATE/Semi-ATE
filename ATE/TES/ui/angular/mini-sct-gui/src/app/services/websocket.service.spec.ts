import { TestBed } from '@angular/core/testing';
import { WebsocketService } from './websocket.service';
import { MockServerService } from './mockserver.service';

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
      let nextArguments: any;
      service.connect('127.0.0.1');
      // As we nned a function here we have to disable the only-arrow-functions rule here
      // the reason is that the this context, i.e. execution context is different from function
      // and arrow functions
      // tslint:disable:only-arrow-functions
      let spySubject = spyOn((service as any).subject, 'next').and.callFake(function () {
        nextArguments = arguments[0];
      });
      // tslint:enable:only-arrow-functions

      service.send({key: 'Value'});
      expect(nextArguments.key).toEqual('Value');
    });
  });
});
