import {statusEqual, Status, SystemState} from 'src/app/models/status.model';

describe('statusEqaul', () => {
  it('should return false in case that first status element is undefined', () => {
    const status1: Status = undefined;
    const status2: Status = {
      deviceId: 'connecting',
      env: 'connecting',
      handler: 'connecting',
      time: 'connecting',
      sites: new Array<string>(),
      program: '',
      log: '',
      state: SystemState.connecting,
      reason: '',
      lotNumber: ''
    };
    expect(statusEqual(status1, status2)).toBeFalse();
  });

  it('should return false in case that second status element is undefined', () => {
    const status1: Status = {
      deviceId: 'connecting',
      env: 'connecting',
      handler: 'connecting',
      time: 'connecting',
      sites: new Array<string>(),
      program: '',
      log: '',
      state: SystemState.connecting,
      reason: '',
      lotNumber: ''
    };
    const status2: Status = undefined;
    expect(statusEqual(status1, status2)).toBeFalse();
  });

  it('should return false in case that one element is null', () => {
    const status1: Status = {
      deviceId: 'connecting',
      env: 'connecting',
      handler: 'connecting',
      time: 'connecting',
      sites: new Array<string>(),
      program: '',
      log: '',
      state: SystemState.connecting,
      reason: '',
      lotNumber: ''
    };
    const status2: Status = null;
    expect(statusEqual(status1, status2)).toBeFalse();
  });

  it('should return true in case that both status elements are "undefined" or "null"', () => {
    expect(statusEqual(undefined, undefined)).toBeTrue();
    expect(statusEqual(null, null)).toBeTrue();
  });

  describe('option ignoreTime', () => {
    it('should return false in case that ignoreTime is set to "false" and the two status values only differ on attribute "time"', () => {
      const status1: Status = {
        deviceId: 'connecting',
        env: 'connecting',
        handler: 'connecting',
        time: 'connecting',
        sites: new Array<string>(),
        program: '',
        log: '',
        state: SystemState.connecting,
        reason: '',
        lotNumber: ''
      };
      const status2: Status = {
        deviceId: status1.deviceId,
        env: status1.env,
        handler: status1.handler,
        time: '14:20',
        sites: status1.sites,
        program: status1.program,
        log: status1.log,
        state: status1.state,
        reason: status1.reason,
        lotNumber: status1.lotNumber
      };
      expect(statusEqual(status1, status2, false)).toBeFalse();
    });

    it('should return true in case that ignoreTime is set to "true" and the two status values only differ on attribute "time"', () => {
      const status1: Status = {
        deviceId: 'connecting',
        env: 'connecting',
        handler: 'connecting',
        time: 'connecting',
        sites: new Array<string>(),
        program: '',
        log: '',
        state: SystemState.connecting,
        reason: '',
        lotNumber: ''
      };
      const status2: Status = {
        deviceId: status1.deviceId,
        env: status1.env,
        handler: status1.handler,
        time: '14:20',
        sites: status1.sites,
        program: status1.program,
        log: status1.log,
        state: status1.state,
        reason: status1.reason,
        lotNumber: status1.lotNumber
      };
      expect(statusEqual(status1, status2, true)).toBeTrue();
    });
  });
});