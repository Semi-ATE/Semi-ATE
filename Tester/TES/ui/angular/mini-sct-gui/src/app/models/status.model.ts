export enum SystemState {
  connecting = 'connecting',
  error = 'error',
  softerror = 'softerror',
  initialized = 'initialized',
  loading = 'loading',
  ready = 'ready',
  testing = 'testing',
  paused = 'paused',
  unloading = 'unloading',
  waitingForBinTable = 'waitingforbintable'
}

export interface Status {
  deviceId: string;
  env: string;
  handler: string;
  time: string;
  sites: Array<string>;
  program: string;
  log: string;
  state: SystemState;
  reason: string;
  lotNumber: string;
}

export function statusEqual(status1: Status, status2: Status, ignoreTime: boolean = true): boolean {
  let equal = true;
  if (status1 && !status2) {
    return false;
  } else if (!status1 && status2) {
    return false;
  } else if (!status1 && !status2) {
    return true;
  } else {
    Object.keys(status1).forEach( k => {
      if( k === 'sites' ) {
        if (status1[k].length !== status2[k].length) {
          equal = false;
        } else {
          equal = equal && status1[k].every( (e,i) => e === status2[k][i]);
        }
      } else if ( k === 'time') {
        if (!ignoreTime)
          equal = equal && status1[k] === status2[k];
      } else {
        equal = equal && status1[k] === status2[k];
      }
    });
  }
  return equal;
}
