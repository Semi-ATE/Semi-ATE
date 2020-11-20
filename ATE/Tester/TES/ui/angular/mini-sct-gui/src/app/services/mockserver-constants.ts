import {formatDate } from '@angular/common';
import { LogLevel, TestOptionType } from '../models/usersettings.model';
import { MessageTypes } from './appstate.service';

export const MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID = 'mock-server-service';

export const MESSAGE_WHEN_SERVER_START = {
  type: MessageTypes.Status,
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
  type: MessageTypes.Status,
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
  type: MessageTypes.Status,
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
  type: MessageTypes.Status,
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'error',
    error_message: 'Error message',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_SOFTERROR = {
  type: MessageTypes.Status,
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'softerror',
    error_message: 'One of the control applications crashed',
    env: 'F1'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_LOADING = {
  type: MessageTypes.Status,
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
  type: MessageTypes.Status,
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
  type: MessageTypes.Status,
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['A', 'B', 'C', 'D'],
    state: 'ready',
    error_message: '',
    env: 'F1',
    handler: 'Geringer',
    lot_number: '123456.123'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_TESTING = {
  type: MessageTypes.Status,
  payload: {
    device_id: 'MiniSCT',
    systemTime: 'Jul 6, 2020, 12:29:21 PM',
    sites: ['A'],
    state: 'testing',
    error_message: '',
    env: 'F1',
    handler: 'invalid',
    lot_number: '123456.123'
  }
};

export const MESSAGE_WHEN_SYSTEM_STATUS_WAITING = {
  type: MessageTypes.Status,
  payload: {
    device_id: 'MiniSCT',
    systemTime: 'Jul 6, 2020, 12:29:21 PM',
    sites: ['0', '1'],
    state: 'waitingforbintable',
    error_message: '',
    env: 'F1',
    handler: 'invalid',
    lot_number: '123456.123'
  }
};

export const TEST_RESULT_SITE_0_TEST_PASSED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 0
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 0,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 0,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 3.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '10',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 1.0,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 0,
      PART_FLG: 0,
      NUM_TEST: 2,
      HARD_BIN: 1,
      SOFT_BIN: 1,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 1',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_0_TEST_FAILED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 0
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 0,
      TEST_FLG: 8,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '1',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 0,
      TEST_FLG: 8,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '2',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.5,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 0,
      PART_FLG: 8,
      NUM_TEST: 2,
      HARD_BIN: 5,
      SOFT_BIN: 5,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 2',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_1_TEST_PASSED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 1
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 1,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 1,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 3.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 1.0,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 1,
      PART_FLG: 0,
      NUM_TEST: 2,
      HARD_BIN: 2,
      SOFT_BIN: 2,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 3',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_1_TEST_FAILED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 1
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 1,
      TEST_FLG: 3,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '1',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 1,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '2',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.5,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 1,
      PART_FLG: 8,
      NUM_TEST: 2,
      HARD_BIN: 5,
      SOFT_BIN: 5,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 4',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_2_TEST_PASSED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 2
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 2,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 2,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 3.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 1.0,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 2,
      PART_FLG: 0,
      NUM_TEST: 2,
      HARD_BIN: 1,
      SOFT_BIN: 1,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 5',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_2_TEST_FAILED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 2
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 2,
      TEST_FLG: 2,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '1',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 2,
      TEST_FLG: 7,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '2',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.5,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 2,
      PART_FLG: 8,
      NUM_TEST: 2,
      HARD_BIN: 5,
      SOFT_BIN: 5,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 6',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_3_TEST_PASSED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 3
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 3,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 3,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 3.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '',
      OPT_FLAG: ['0', '0', '0', '0', '0', '0', '0', '0'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 1.0,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 3,
      PART_FLG: 0,
      NUM_TEST: 2,
      HARD_BIN: 2,
      SOFT_BIN: 2,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 7',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

export const TEST_RESULT_SITE_3_TEST_FAILED = {
  type: MessageTypes.Testresult,
  payload: [
    {
      type: 'PIR',
      HEAD_NUM: 0,
      SITE_NUM: 3
    },
    {
      type: 'PTR',
      TEST_NUM: 1,
      HEAD_NUM: 0,
      SITE_NUM: 3,
      TEST_FLG: 0,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'Isup@2.4V',
      ALARM_ID: '1',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.75,
      HI_LIMIT: 4.0,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PTR',
      TEST_NUM: 2,
      HEAD_NUM: 0,
      SITE_NUM: 3,
      TEST_FLG: 5,
      PARM_FLG: [],
      RESULT: 2.0,
      TEST_TXT: 'testIsup@3V',
      ALARM_ID: '2',
      OPT_FLAG: ['1', '1', '1', '1', '1', '1', '1', '1'],
      RES_SCALING: 0,
      LLM_SCAL: 0,
      HLM_SCAL: 0,
      LO_LIMIT: 2.5,
      HI_LIMIT: 3.5,
      UNITS: 'mA',
      C_RESFMT: '',
      C_LLMFMT: '',
      C_HLMFMT: '',
      LO_SPEC: 0.0,
      HI_SPEC: 0.0,
    },
    {
      type: 'PRR',
      HEAD_NUM: 0,
      SITE_NUM: 3,
      PART_FLG: 8,
      NUM_TEST: 2,
      HARD_BIN: 5,
      SOFT_BIN: 5,
      X_COORD: 0,
      Y_COORD: 0,
      TEST_T: 2001,
      PART_ID: 'Part 7',
      PART_TXT: '',
      PART_FIX: [],
    },
  ]
};

const PIR_SITE_0 = {
  type: 'PIR',
  HEAD_NUM: 0,
  SITE_NUM: 0
};

const PIR_SITE_1 = {
  type: 'PIR',
  HEAD_NUM: 0,
  SITE_NUM: 1
};

const PTR_ISUP_SITE_0 = {
  type: 'PTR',
  TEST_NUM: 1,
  HEAD_NUM: 0,
  SITE_NUM: 0,
  TEST_FLG: 0,
  PARM_FLG: 0,
  RESULT: 2.0,
  TEST_TXT: 'Isup@2.4V',
  ALARM_ID: '1',
  OPT_FLAG: 0,
  RES_SCALING: 0,
  LLM_SCAL: 0,
  HLM_SCAL: 0,
  LO_LIMIT: 2.75,
  HI_LIMIT: 4.0,
  UNITS: 'mA',
  C_RESFMT: '',
  C_LLMFMT: '',
  C_HLMFMT: '',
  LO_SPEC: 0.0,
  HI_SPEC: 0.0,
};

const PTR_ISUP_SITE_1 = {
  type: 'PTR',
  TEST_NUM: 1,
  HEAD_NUM: 0,
  SITE_NUM: 1,
  TEST_FLG: 0,
  PARM_FLG: 0,
  RESULT: 2.0,
  TEST_TXT: 'Isup@2.4V',
  ALARM_ID: '1',
  OPT_FLAG: 0,
  RES_SCALING: 0,
  LLM_SCAL: 0,
  HLM_SCAL: 0,
  LO_LIMIT: 2.75,
  HI_LIMIT: 4.0,
  UNITS: 'mA',
  C_RESFMT: '',
  C_LLMFMT: '',
  C_HLMFMT: '',
  LO_SPEC: 0.0,
  HI_SPEC: 0.0,
};

const PTR_TEST_ISUP_SITE_0 = {
  type: 'PTR',
  TEST_NUM: 2,
  HEAD_NUM: 0,
  SITE_NUM: 0,
  TEST_FLG: 1,
  PARM_FLG: 0,
  RESULT: 2.0,
  TEST_TXT: 'testIsup@3V',
  ALARM_ID: '2',
  OPT_FLAG: 0,
  RES_SCALING: 0,
  LLM_SCAL: 0,
  HLM_SCAL: 0,
  LO_LIMIT: 2.5,
  HI_LIMIT: 3.5,
  UNITS: 'mA',
  C_RESFMT: '',
  C_LLMFMT: '',
  C_HLMFMT: '',
  LO_SPEC: 0.0,
  HI_SPEC: 0.0,
};

const PTR_TEST_ISUP_SITE_1 = {
  type: 'PTR',
  TEST_NUM: 2,
  HEAD_NUM: 0,
  SITE_NUM: 1,
  TEST_FLG: 1,
  PARM_FLG: 0,
  RESULT: 2.0,
  TEST_TXT: 'testIsup@3V',
  ALARM_ID: '2',
  OPT_FLAG: 0,
  RES_SCALING: 0,
  LLM_SCAL: 0,
  HLM_SCAL: 0,
  LO_LIMIT: 2.5,
  HI_LIMIT: 3.5,
  UNITS: 'mA',
  C_RESFMT: '',
  C_LLMFMT: '',
  C_HLMFMT: '',
  LO_SPEC: 0.0,
  HI_SPEC: 0.0,
};

const PRR_SITE_0 = {
  type: 'PRR',
  HEAD_NUM: 0,
  SITE_NUM: 0,
  PART_FLG: 8,
  NUM_TEST: 2,
  HARD_BIN: 5,
  SOFT_BIN: 5,
  X_COORD: 0,
  Y_COORD: 0,
  TEST_T: 2001,
  PART_ID: 'Part 1',
  PART_TXT: '',
  PART_FIX: [],
};

const PRR_SITE_1 = {
  type: 'PRR',
  HEAD_NUM: 0,
  SITE_NUM: 1,
  PART_FLG: 8,
  NUM_TEST: 2,
  HARD_BIN: 5,
  SOFT_BIN: 5,
  X_COORD: 0,
  Y_COORD: 0,
  TEST_T: 2001,
  PART_ID: 'Part 4',
  PART_TXT: '',
  PART_FIX: [],
};

export const TEST_RESULTS_SITE_1_AND_2 = {
  type: MessageTypes.Testresults,
  payload: [
    [
      PIR_SITE_0,
      PTR_ISUP_SITE_0,
      PTR_TEST_ISUP_SITE_0,
      {...PRR_SITE_0, PART_ID: 'Part 1'},
    ],
    [
      PIR_SITE_1,
      PTR_ISUP_SITE_1,
      PTR_TEST_ISUP_SITE_1,
      {...PRR_SITE_1, PART_ID: 'Part 2'},
    ],
    [
      PIR_SITE_0,
      PTR_ISUP_SITE_0,
      PTR_TEST_ISUP_SITE_0,
      {...PRR_SITE_0, PART_ID: 'Part 3'},
    ],
    [
      PIR_SITE_1,
      PTR_ISUP_SITE_1,
      PTR_TEST_ISUP_SITE_1,
      {...PRR_SITE_1, PART_ID: 'Part 4'},
    ]
  ]
};

export const USER_SETTINGS_FROM_SERVER = {
  type: MessageTypes.Usersettings,
  payload: {
    testoptions: [
      {
        name: TestOptionType.stopOnFail,
        active: true,
        value: -1,
      },
      {
        name: TestOptionType.stopAtTestNumber,
        active: false,
        value: 4
      },
      {
        name: TestOptionType.triggerSiteSpecific,
        active: true,
        value: 80
      },
    ],
    loglevel: LogLevel.Warning
  }
};

export const LOG_ENTRIES = {
  type: MessageTypes.Logdata,
  payload: [
    {
      date: '07/09/2020 03:30:50 PM',
      type: 'DEBUG',
      description: 'testprogram information: {"USERTEXT": "F1N", "TEMP": "25", "TESTERPRG": "825A", "PROGRAM_DIR": "C:/Users/abdou.AWINIA/new11/src/HW0/PR/new11_HW0_PR_fdf_P_1.py", "TESTER": "SCT-81-1F", "TESTER_ALIAS": "SCT81_1"}',
      source: 'testapp'
    },
    {
      date: '07/09/2020 03:30:50 PM',
      type: 'INFO',
      description: 'Master state is loading',
      source: 'master'
    },
    {
      date: '07/09/2020 03:30:50 PM',
      type: 'WARNING',
      description: 'Control 0 state is loading',
      source: 'control 0'
    },
    {
      date: '07/09/2020 03:30:50 PM',
      type: 'ERROR',
      description: 'Control 0 state is busy',
      source: 'control 0'
    }
  ]
};

export const LOG_FILE = {
  type: MessageTypes.Logfile,
  payload: {
    filename: 'test.txt',
    content: 'das ist ein langer string | das auch ü üpsad+üaso\ndas sollte in der zweiten Zeile stehen\ndas in der dritten'
  }
};

export const CONNECTION_ID = {
  type: MessageTypes.ConnectionId,
  payload: {
    connectionid: 'UU45237'
  }
};

const YIELD_DATA_GENERAL = [
  {
    name: 'First Grade',
    siteid: '-1',
    value: 10.0,
    count: 30
  },
  {
    name: 'Second Grade',
    siteid: '-1',
    value: 25.0,
    count: 70
  },
  {
    name: 'Third Grade',
    siteid: '-1',
    value: 25.0,
    count: 150
  },
  {
    name: 'Fourth Grade',
    siteid: '-1',
    value: 40.0,
    count: 50
  },
  {
    name: 'Sum',
    siteid: '-1',
    value: 100,
    count: 300
   }
];

const YIELD_DATA_SITE_0 = [
  {
    name: 'First Grade',
    siteid: '0',
    value: 10.0,
    count: 25
  },
  {
    name: 'Second Grade',
    siteid: '0',
    value: 10.0,
    count: 25
  },
  {
    name: 'Third Grade',
    siteid: '0',
    value: 50.0,
    count: 25
  },
  {
    name: 'Fourth Grade',
    siteid: '0',
    value: 30,
    count: 25
  },
  {
    name: 'Sum',
    siteid: '0',
    value: 100,
    count: 100
   }
];

const YIELD_DATA_SITE_1 = [
  {
    name: 'First Grade',
    siteid: '1',
    value: 60.0,
    count: 250
  },
  {
    name: 'Second Grade',
    siteid: '1',
    value: 10.0,
    count: 250
  },
  {
    name: 'Third Grade',
    siteid: '1',
    value: 20.0,
    count: 400
  },
  {
    name: 'Fourth Grade',
    siteid: '1',
    value: 10.0,
    count: 400
  },
  {
    name: 'Sum',
    siteid: '1',
    value: 100,
    count: 1300
   }
];

const YIELD_DATA_SITE_2 = [
  {
    name: 'First Grade',
    siteid: '2',
    value: 30.6,
    count: 700
  },
  {
    name: 'Second Grade',
    siteid: '2',
    value: 9.4,
    count: 15
  },
  {
    name: 'Third Grade',
    siteid: '2',
    value: 10.0,
    count: 85
  },
  {
    name: 'Fourth Grade',
    siteid: '2',
    value: 50.0,
    count: 20
  },
  {
    name: 'Sum',
    siteid: '2',
    value: 100,
    count: 820
   },
];

const YIELD_DATA_SITE_3 = [
  {
    name: 'Site 3 - First Grade',
    siteid: '3',
    value: 61.0,
    count: 140
  },
  {
    name: 'Site 3 - Second Grade',
    siteid: '3',
    value: 9.0,
    count: 460
  },
  {
    name: 'Third Grade',
    siteid: '3',
    value: 10.0,
    count: 85
  },
  {
    name: 'Fourth Grade',
    siteid: '3',
    value: 20.0,
    count: 15
  },
  {
    name: 'Sum',
    siteid: '3',
    value: 100,
    count: 700
  }
];

export const YIELD_ENTRIES = {
  type: MessageTypes.Yield,
  payload: [
    ...YIELD_DATA_GENERAL,
    ...YIELD_DATA_SITE_0,
    ...YIELD_DATA_SITE_1,
    ...YIELD_DATA_SITE_2,
    ...YIELD_DATA_SITE_3
  ]
};

