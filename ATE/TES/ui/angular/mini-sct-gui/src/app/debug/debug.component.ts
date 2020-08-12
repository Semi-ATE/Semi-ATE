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
      description: 'Generate Console Entry',
      value: 'Console'
    }
  ];

  constructor(private readonly mss: MockServerService) {
  }

  ngOnInit() {
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
      case SystemState.unloading:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_UNLOADING]);
        break;
      case 'Console':
        this.mss.setMessages([constants.TEST_APP_MESSAGE_SITE_7_TESTING])
        break;
    }
  }
}
