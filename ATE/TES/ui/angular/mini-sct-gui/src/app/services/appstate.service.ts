import { Injectable } from '@angular/core';
import { AppState } from './../app.state';
import { Store } from '@ngrx/store';
import { Status, statusEqual } from './../models/status.model';
import { CommunicationService } from './communication.service';
import * as StatusActions from './../actions/status.actions';
import * as ResultActions from './../actions/result.actions';
import * as ConsoleActions from './../actions/console.actions';
import * as UserSettingsActions from './../actions/usersettings.actions';
import { formatDate } from '@angular/common';
import { ConsoleEntry } from '../models/console.model';
import { StdfRecord, StdfRecordType, StdfRecordValueType, StdfRecordLabelType} from 'src/app/stdf/stdf-stuff';
import { Subject } from 'rxjs';
import { TestOptionSetting, TestOptionType } from '../models/usersettings.model';
import { TestOptionValue } from '../system-control/test-option/test-option.component';

export enum MessageTypes {
  Cmd = 'cmd',
  Status = 'status',
  Testresult = 'testresult',
  Testresults = 'testresults',
  Usersettings = 'usersettings'
}

@Injectable({
  providedIn: 'root'
})
export class AppstateService {

  rebuildRecords$: Subject<boolean>;
  newRecordReceived$: Subject<StdfRecord[]>;
  stdfRecords: StdfRecord[];
  systemTime: string;
  private lastStatus: Status;
  private statusChanged: boolean;

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.stdfRecords = [];
    this.newRecordReceived$ = new Subject<StdfRecord[]>();
    this.rebuildRecords$ = new Subject<boolean>();
    communicationService.message.subscribe(msg => this.handleServerMessage(msg));
  }

  private handleServerMessage(serverMessage: any) {
    // update system status must be called first
    this.updateSystemStatus(serverMessage);
    this.updateResults(serverMessage);
    this.updateConsole(serverMessage);
    this.updateUserSettings(serverMessage);
  }

  private updateSystemStatus(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Status && serverMessage.payload) {
      let receivedStatus: Status = {
        deviceId : serverMessage.payload.device_id,
        env: serverMessage.payload.env,
        handler: serverMessage.payload.handler,
        time: serverMessage.payload.systemTime,
        sites: serverMessage.payload.sites,
        program: serverMessage.payload.program,
        log: serverMessage.payload.log,
        state: serverMessage.payload.state,
        reason: serverMessage.payload.error_message,
        lotNumber: serverMessage.payload.lot_number,
      };
      this.statusChanged = !statusEqual(receivedStatus, this.lastStatus);
      this.lastStatus = receivedStatus;
      this.systemTime = serverMessage.payload.systemTime;
      this.store.dispatch(new StatusActions.UpdateStatus(receivedStatus));
    }
  }

  private updateBinStatus(record: StdfRecord) {
    if (record?.type === StdfRecordType.Prr) {
      this.store.dispatch(new ResultActions.AddResult(record));
    }
  }

  private updateResults(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Testresult) {
      // get prr record for determining bin and pas/fail informations
      if (serverMessage.payload && serverMessage.payload.length > 0) {
        let newReceivedRecords: StdfRecord[] = [];
        serverMessage.payload.forEach(e => {
          let record: StdfRecord = {
            type : e.type,
            values : Object.entries(e).filter( ([k,v]) => k !== 'type')
              .map(([k,v]) => [k as StdfRecordLabelType, v as StdfRecordValueType]) as [StdfRecordLabelType, StdfRecordValueType][]
          };
          this.stdfRecords.push(record);
          newReceivedRecords.push(record);
          this.updateBinStatus(record);
        });
        this.newRecordReceived$.next(newReceivedRecords);
      }
    }
    if (serverMessage.type === MessageTypes.Testresults) {
      if (serverMessage.payload && serverMessage.payload.length >=0) {
        // clear/delete all stored records
        this.stdfRecords = [];
        serverMessage.payload.forEach(e => {
          if (e.length > 0) {
            e.forEach(a => {
              let record: StdfRecord = {
                type : a.type,
                values : Object.entries(a).filter( ([k,v]) => k !== 'type')
                  .map(([k,v]) => [k as StdfRecordLabelType, v as StdfRecordValueType]) as [StdfRecordLabelType, StdfRecordValueType][]
              };
              this.stdfRecords.push(record);
              this.updateBinStatus(record);
            });
          }
        });
        this.rebuildRecords$.next(true);
      }
    }
  }

  private updateConsole(serverMessage: any) {
    if (serverMessage) {
      if (serverMessage.type) {
        let entry: ConsoleEntry = {
          description: '',
          date: this.systemTime || 'unknown',
          type: serverMessage.type,
          json: ''};
        if (serverMessage.type === MessageTypes.Status && this.statusChanged) {
          entry.description = `Entering state '${serverMessage.payload.state}'. ${serverMessage.payload.error_message}`;
        } else {
          switch(serverMessage.type) {
            case MessageTypes.Testresult:
              entry.description = `New part result for site ${serverMessage.payload?.[0]?.SITE_NUM} arrived`;
              break;
            case MessageTypes.Testresults:
              entry.description = `Server send all stored part results (${serverMessage.payload.length})`;
              break;
            case MessageTypes.Usersettings:
              entry.description = `Server send current user settings`;
              break;
          }
        }
        if (entry.description !== '') {
          entry.json = serverMessage;
          this.store.dispatch(new ConsoleActions.Add(entry));
        }
      }
    }
  }

  private updateUserSettings(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Usersettings) {
      if ( serverMessage.payload && serverMessage.payload.length > 0) {
        let testOptions: TestOptionSetting[] = serverMessage.payload.map(e => {
          return {
            type: e.name as TestOptionType,
            value: {
              active: e.active,
              value: e.value
            } as TestOptionValue
          } as TestOptionSetting;
        });
        this.store.dispatch(new UserSettingsActions.Set(testOptions));
      }
    }
  }
}
