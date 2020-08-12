export enum SystemState {
  connecting = 'connecting',
  error = 'error',
  initialized = 'initialized',
  loading = 'loading',
  ready = 'ready',
  testing = 'testing',
  paused = 'paused',
  unloading = 'unloading'
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
}
