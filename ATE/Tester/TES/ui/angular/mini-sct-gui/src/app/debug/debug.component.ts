import { Component, OnInit } from '@angular/core';
import { SystemState } from 'src/app/models/status.model';
import { MockServerService } from 'src/app/services/mockserver.service';
import * as constants from 'src/app/services/mockserver-constants';
import { DropdownConfiguration } from '../basic-ui-elements/dropdown/dropdown-config';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';
import { MessageTypes } from '../services/appstate.service';

@Component({
  selector: 'app-debug',
  templateUrl: './debug.component.html',
  styleUrls: ['./debug.component.scss']
})
export class DebugComponent implements OnInit {

  readonly STATES = [
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
      description: 'Waiting for Bin-Table',
      value: SystemState.waitingForBinTable
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
    },
    {
      description: 'Generate yield entries',
      value: 'Yield'
    },
    {
      description: 'Generate lot data',
      value: 'Lotdata'
    },
    {
      description: 'Generate bin entries',
      value: 'BinTable'
    },
    {
      description: 'Max bin table',
      value: 'MaxBinTable'
    }
  ];

  mockdataDropdownConfig: DropdownConfiguration;
  captionCardConfiguration: CardConfiguration;
  mockdataCardConfiguration: CardConfiguration;

  constructor(private readonly mss: MockServerService) {
    this.mockdataDropdownConfig = new DropdownConfiguration();
    this.captionCardConfiguration = new CardConfiguration();
    this.mockdataCardConfiguration = new CardConfiguration();
  }

  ngOnInit() {
    this.initMockdataDropdown();
    this.initCardElements();
    this.sendMockMessage('Result');
  }

  sendMockMessage(messageType: string) {
    this.mss.setRepeatMessages(false);
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
      case SystemState.waitingForBinTable:
        this.mss.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_WAITING]);
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
        this.mss.setMessages([constants.USER_SETTINGS_FROM_SERVER]);
        break;
      case 'ReloadResults':
        this.mss.setMessages([constants.TEST_RESULTS_SITE_1_AND_2]);
        break;
      case 'Logfile':
        this.mss.setMessages([constants.LOG_FILE]);
        break;
      case 'Logentries':
        this.mss.setMessages([constants.LOG_ENTRIES]);
        break;
      case 'Yield':
        this.mss.setMessages([constants.YIELD_ENTRIES]);
        break;
      case 'Lotdata':
        this.mss.setMessages([constants.LOT_DATA]);
        break;
      case 'BinTable':
        this.mss.setMessages([constants.BIN_ENTRIES]);
        break;
      case 'MaxBinTable':
        this.mss.setMessages([
          {
            type: MessageTypes.Status,
            payload: {
              device_id: 'MiniSCT',
              systemTime: 'Jul 6, 2020, 12:29:21 PM',
              sites: [
                'A', 'B', 'C', 'D',
                'E', 'F', 'G', 'H',
                'I', 'J', 'K', 'L',
                'M', 'N', 'O', 'P',
              ],
              state: 'testing',
              error_message: '',
              env: 'F1',
              handler: 'invalid',
              lot_number: '123456.123'
            }
          },
          constants.BIN_TABLE_MAX_SITES
        ]);
        break;
    }
  }

  private initMockdataDropdown(): void {
    let items = this.STATES.map(e => e);
    this.mockdataDropdownConfig.initDropdown('Select Mockdata', false, items, 0);
  }

  private initCardElements(): void {
    this.captionCardConfiguration.cardStyle = CardStyle.COLUMN_STYLE_FOR_COMPONENT;
    this.captionCardConfiguration.labelText = 'Debug Area';
    this.mockdataCardConfiguration.cardStyle = CardStyle.COLUMN_STYLE;
    this.mockdataCardConfiguration.shadow = true;
  }
}
