import { Injectable, OnDestroy } from '@angular/core';
import { AppState } from './../app.state';
import { Store } from '@ngrx/store';
import { Status, statusEqual } from './../models/status.model';
import { CommunicationService } from './communication.service';
import * as StatusActions from './../actions/status.actions';
import * as ResultActions from './../actions/result.actions';
import * as ConsoleActions from './../actions/console.actions';
import * as UserSettingsActions from './../actions/usersettings.actions';
import { ConsoleEntry } from '../models/console.model';
import { StdfRecord, StdfRecordType, StdfRecordPropertyValue, PrrRecord } from 'src/app/stdf/stdf-stuff';
import { Subject, Subscription } from 'rxjs';
import { TestOptionSetting, TestOptionType } from '../models/usersettings.model';
import { TestOptionValue } from '../system-control/test-option/test-option.component';
import { saveAs } from 'file-saver';

export enum MessageTypes {
  Cmd = 'cmd',
  Status = 'status',
  Testresult = 'testresult',
  Testresults = 'testresults',
  Usersettings = 'usersettings',
  Logdata = 'logs',
  Logfile = 'logfile'
}

@Injectable({
  providedIn: 'root'
})
export class AppstateService implements OnDestroy {

  rebuildRecords$: Subject<boolean>;
  newRecordReceived$: Subject<StdfRecord[]>;
  stdfRecords: StdfRecord[];
  systemTime: string;
  private lastStatus: Status;
  private statusChanged: boolean;
  private readonly subscriptionCommunication: Subscription;

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.stdfRecords = [];
    this.newRecordReceived$ = new Subject<StdfRecord[]>();
    this.rebuildRecords$ = new Subject<boolean>();
    this.subscriptionCommunication = communicationService.message.subscribe(msg => this.handleServerMessage(msg));
  }

  ngOnDestroy(): void {
    this.subscriptionCommunication.unsubscribe();
  }

  private handleServerMessage(serverMessage: any) {
    // update system status must be called first
    this.updateSystemStatus(serverMessage);
    this.updateResults(serverMessage);
    this.updateConsole(serverMessage);
    this.updateUserSettings(serverMessage);
    this.handleLogfile(serverMessage);
  }

  private updateSystemStatus(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Status && serverMessage.payload) {
      let receivedStatus: Status = {
        deviceId: serverMessage.payload.device_id,
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
      this.store.dispatch(StatusActions.updateStatus({status:receivedStatus}));
    }
  }

  private updateBinStatus(record: StdfRecord) {
    if (record.type === StdfRecordType.Prr) {
      let prr = new PrrRecord();
      prr.values = record.values;
      this.store.dispatch(ResultActions.addResult({prr}));
    }
  }

  private updateResults(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Testresult) {
      let newReceivedRecords: StdfRecord[] = [];
      serverMessage.payload.forEach(e => {
        let record: StdfRecord = {
          type: e.type,
          values: Object.entries(e).filter(([k, v]) => k !== 'type')
            .map(([k, v]) => {
              return {
                key: k,
                value: v as StdfRecordPropertyValue
              };
            })
        };
        this.stdfRecords.push(record);
        newReceivedRecords.push(record);
        this.updateBinStatus(record);
      });
      this.newRecordReceived$.next(newReceivedRecords);
    }
    if (serverMessage.type === MessageTypes.Testresults) {
      // clear/delete all stored records
      this.stdfRecords = [];
      serverMessage.payload.forEach(e => {
        if (e.length > 0) {
          e.forEach(a => {
            let record: StdfRecord = {
              type: a.type,
              values: Object.entries(a).filter(([k, v]) => k !== 'type')
                .map(([k, v]) => {
                  return {
                    key: k,
                    value: v as StdfRecordPropertyValue
                  };
                })
            };
            this.stdfRecords.push(record);
            this.updateBinStatus(record);
          });
        }
      });
      this.rebuildRecords$.next(true);
    }
  }

  private updateConsole(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Logdata) {
      let entriesToAdd: ConsoleEntry[] = [];
      serverMessage.payload.forEach(
        e => {
          entriesToAdd.push({
            description: e.description,
            date: e.date,
            type: e.type,
          });
        }
      );
      this.store.dispatch(ConsoleActions.addConsoleEntry({entries: entriesToAdd}));
    }
  }

  private updateUserSettings(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Usersettings) {
      let testOptions: TestOptionSetting[] = serverMessage.payload.map(e => {
        return {
          type: e.name as TestOptionType,
          value: {
            active: e.active,
            value: e.value
          } as TestOptionValue
        } as TestOptionSetting;
      });
      this.store.dispatch(UserSettingsActions.setSettings({settings:testOptions}));
    }
  }

  private handleLogfile(serverMessage: any) {
    if (serverMessage.type === MessageTypes.Logfile) {
      var file = new File([serverMessage.payload.content],
         serverMessage.payload.filename,
         {type: 'text/plain;charset=utf-8'});
      saveAs(file);
    }
  }
}
