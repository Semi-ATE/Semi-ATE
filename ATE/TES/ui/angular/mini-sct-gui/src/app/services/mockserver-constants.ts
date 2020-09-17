import {formatDate } from '@angular/common';
import { TestOptionType } from '../models/usersettings.model';

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

export const MESSAGE_WHEN_SYSTEM_STATUS_SOFTERROR = {
  type: 'status',
  payload: {
    device_id: 'MiniSCT',
    systemTime: formatDate(Date.now(), 'medium', 'en-US'),
    sites: ['0'],
    state: 'softerror',
    error_message: 'On of the control applications crashed',
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
    sites: ['A', 'B', 'C', 'D'],
    state: 'ready',
    error_message: '',
    env: 'F1',
    handler: 'Geringer',
    lot_number: '123456.123'
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
    handler: 'invalid',
    lot_number: '123456.123'
  }
};

export const TEST_RESULT_SITE_0_TEST_PASSED = {
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '0'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      SITE_NUM: 1,
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresult',
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
      TEST_FLG: ['0', '1', '0', '0', '0', '0', '0', '1'],
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
  type: 'testresults',
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
  type: 'usersettings',
  payload: [
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
  ]
};