import { Component, OnInit } from '@angular/core';
import { SystemState } from 'src/app/models/status.model';
import { MockServerService } from 'src/app/services/mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';

@Component({
  selector: 'app-debug',
  templateUrl: './debug.component.html',
  styleUrls: ['./debug.component.scss']
})
export class DebugComponent implements OnInit {

  readonly STATES: any = [
    {
      description: 'Connecting',
      value: SystemState.connecting
    },
    {
      description : 'Tester initialized',
      value: SystemState.initialized
    },
    {
      description : 'Loading Test Program',
      value: SystemState.loading
    },
    {
      description : 'Ready for DUT Test',
      value: SystemState.ready
    },
    {
      description : 'Test Execution',
      value: SystemState.testing
    },
    {
      description : 'Unloading Test Program',
      value: SystemState.unloading
    },
    {
      description: 'Error',
      value: SystemState.error
    },
    {
      description: 'Softerror',
      value: SystemState.softerror
    },
    {
      description: 'Generate Test Result',
      value: 'Result'
    },
    {
      description: 'Set test options',
      value: 'TestOptions'
    },
    {
      description: 'Reload Results',
      value: 'ReloadResults'
    },
    {
      description: 'Download Logfile',
      value: 'Logfile'
    },
    {
      description: 'Generate log entries',
      value: 'Logentries'
    }

  ];

  constructor(private readonly mss: MockServerService) {
  }

  ngOnInit() {
    this.sendMockMessage('Result');
  }

  sendMockMessage(messageType: string) {
    switch (messageType) {
      case SystemState.connecting:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_CONNECTING]);
        break;
      case SystemState.initialized:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED]);
        break;
      case SystemState.ready:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_READY]);
        break;
      case SystemState.loading:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_LOADING]);
        break;
      case SystemState.testing:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_TESTING]);
        break;
      case SystemState.error:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_ERROR]);
        break;
      case SystemState.softerror:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_SOFTERROR]);
        break;
      case SystemState.unloading:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_UNLOADING]);
        break;
      case 'Result':
        this.mss.setRepeatMessages(true);
        this.mss.setMessages([
          constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
          constants.TEST_RESULT_SITE_0_TEST_PASSED,
          constants.TEST_RESULT_SITE_1_TEST_FAILED,
          constants.TEST_RESULT_SITE_2_TEST_PASSED,
          constants.TEST_RESULT_SITE_3_TEST_FAILED,
          constants.TEST_RESULT_SITE_0_TEST_FAILED,
          constants.TEST_RESULT_SITE_1_TEST_PASSED,
          constants.TEST_RESULT_SITE_2_TEST_FAILED,
          constants.TEST_RESULT_SITE_3_TEST_PASSED,
        ]);
        break;
      case 'TestOptions':
        this.mss.setRepeatMessages(false);
        this.mss.setMessages([constants.USER_SETTINGS_FROM_SERVER]);
        break;
      case 'ReloadResults':
        this.mss.setRepeatMessages(false);
        this.mss.setMessages([constants.TEST_RESULTS_SITE_1_AND_2]);
        break;
      case 'Logfile':
        this.mss.setRepeatMessages(false);
        this.mss.setMessages([constants.LOG_FILE]);
        break;
      case 'Logentries':
        this.mss.setRepeatMessages(false);
        this.mss.setMessages([constants.LOG_ENTRIES]);
        break;
    }
  }
}
