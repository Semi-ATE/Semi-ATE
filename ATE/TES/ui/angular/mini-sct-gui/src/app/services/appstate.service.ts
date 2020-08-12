import { Injectable } from '@angular/core';
import { AppState } from './../app.state';
import { Store } from '@ngrx/store';
import { Status } from './../models/status.model'
import { CommunicationService } from './communication.service';
import * as StatusActions from './../actions/status.actions';
import * as ResultActions from './../actions/result.actions';
import * as ConsoleActions from './../actions/console.actions';
import { formatDate } from '@angular/common';
import { ConsoleEntry } from '../models/console.model';


enum MessageTypes {
  Cmd = 'cmd',
  Status = 'status',
  Testresult = 'testresult'
}

@Injectable({
  providedIn: 'root'
})
export class AppstateService {

  constructor(private communicationService: CommunicationService, private store: Store<AppState>) {
    communicationService.message.subscribe(msg => this.handleServerMessage(msg));
  }

  private handleServerMessage(serverMessage: any) {
    this.updateSystemStatus(serverMessage);
    this.updateResults(serverMessage);
    this.updateConsole(serverMessage);
  }

  private updateSystemStatus(serverMessage: any) {
    if (serverMessage.type === 'status' && serverMessage.payload) {
      let receivedStatus : Status = {
        deviceId : serverMessage.payload.device_id,
        env: serverMessage.payload.env,
        handler: serverMessage.payload.handler,
        time: serverMessage.payload.systemTime,
        sites: serverMessage.payload.sites,
        program: serverMessage.payload.program,
        log: serverMessage.payload.log,
        state: serverMessage.payload.state,
        reason: serverMessage.payload.error_message
      };
      this.store.dispatch(new StatusActions.UpdateStatus(receivedStatus));
    }
  }

  private updateResults(serverMessage: any) {
  }

  private updateConsole(serverMessage: any) {
    if (serverMessage && serverMessage.type === 'mqtt.onmessage' && serverMessage.payload) {
      if (serverMessage.payload.payload)
      {
        const STATE: string = serverMessage.payload.payload.state;
        const TOPIC: string = serverMessage.payload.topic;
        const TYPE: string = serverMessage.payload.payload.type;

        if (STATE && TOPIC && TYPE)
        {
          let description : string;
          if (TYPE === MessageTypes.Status) {
            description = TYPE + ':      ' + STATE;
          } else if (serverMessage.type === MessageTypes.Cmd) {
            description = TYPE + ':     ' + serverMessage.command;
          } else if (serverMessage.type === MessageTypes.Testresult) {
            description = TYPE + ':     ' + serverMessage.testdata;
          } else {
             return; 
          }
          this.addConsoleEntry(description, TOPIC);
        }
      }
    }
  }

  private addConsoleEntry(description: string, topic: string): void {
    if (description && topic) {
      const  ENTRY: ConsoleEntry = {
        date: formatDate(Date.now(), 'medium', 'en-US'),
        topic,
        description
      };
      this.store.dispatch(new ConsoleActions.Add(ENTRY));
    }
  }
}
