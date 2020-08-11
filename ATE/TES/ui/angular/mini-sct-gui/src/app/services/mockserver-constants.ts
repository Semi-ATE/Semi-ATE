import { formatDate } from '@angular/common';

export const BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION = 'ws://localhost:8081/ws';
export const MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID = 'mock-server-service';

export const MESSAGE_WHEN_SERVER_START = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'startup',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_CONNECTING = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'connecting',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'initialized',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_ERROR = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'error',
    error_message: 'Error message',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_LOADING = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'loading',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_UNLOADING = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'unloading',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_READY = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'ready',
    error_message: '',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_TESTING = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: 'Jul 6, 2020, 12:29:21 PM',
    sites: ['0'],
    state: 'testing',
    error_message: '',
    env: 'F1',
    handler: 'invalid'
  }
};

export const CONTROL_APP_MESSAGE_SITE_0_BUSY = {
  type: 'mqtt.onmessage',
  payload: {
    payload: {type: 'status', alive: 1, interface_version: 1, software_version: 1, state: 'busy'},
    qos: 0,
    retain: 0,
    topic: 'ate/MiniSCT/Control/status/site0'
  }
};

export const CONTROL_APP_MESSAGE_SITE_0_TESTING = {
  type: 'mqtt.onmessage',
  payload: {
    payload: {type: 'status', alive: 1, interface_version: 1, software_version: 1, state: 'testing'},
    qos: 0,
    retain: 0,
    topic: 'ate/MiniSCT/Control/status/site0'
  }
};

export const TEST_APP_MESSAGE_SITE_7_BUSY = {
  type: 'mqtt.onmessage',
  payload: {
    payload: {type: 'status', alive: 1, framework_version: 1, test_version: 'N/A', state: 'busy'},
    qos: 0,
    retain: 0,
    topic: 'ate/MiniSCT/TestApp/status/site7'
  }
};

export const TEST_APP_MESSAGE_SITE_7_TESTING = {
  type: 'mqtt.onmessage',
  payload: {
    payload: {type: 'status', alive: 1, framework_version: 1, test_version: 'N/A', state: 'testing'},
    qos: 0,
    retain: 0,
    topic: 'ate/MiniSCT/TestApp/status/site7'
  }
};

export const MASTER_APP_MESSAGE = {
  type: 'mqtt.onmessage',
  payload: {
    payload: {type: 'status', alive: 1, interface_version: 1, state: 'testing'},
    qos: 0,
    retain: 0,
    topic: 'ate/MiniSCT/Master/status'
  }
};

