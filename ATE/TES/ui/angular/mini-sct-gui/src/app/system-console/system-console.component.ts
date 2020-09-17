import { Component, OnInit } from '@angular/core';
import { ButtonConfiguration } from './../basic-ui-elements/button/button-config';
import { AppState } from '../app.state';
import { Store, select } from '@ngrx/store';
import { ConsoleEntry } from '../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { Observable } from 'rxjs';
import { CommunicationService } from '../services/communication.service';

@Component({
  selector: 'app-system-console',
  templateUrl: './system-console.component.html',
  styleUrls: ['./system-console.component.scss']
})
export class SystemConsoleComponent implements OnInit {
  clearConsoleButtonConfig: ButtonConfiguration;
  reloadLogsButtonConfig: ButtonConfiguration;
  getLogFileButtonConfig: ButtonConfiguration;

  consoleEntries$: Observable<ConsoleEntry[]>;

  constructor(private readonly store: Store<AppState>, private readonly communicationService: CommunicationService) {
    this.clearConsoleButtonConfig = new ButtonConfiguration();
    this.reloadLogsButtonConfig = new ButtonConfiguration();
    this.getLogFileButtonConfig = new ButtonConfiguration();
    this.consoleEntries$ = store.pipe(select('consoleEntries'));
  }

  ngOnInit() {
    this.clearConsoleButtonConfig.labelText = 'Clear';
    this.clearConsoleButtonConfig.disabled = false;

    this.reloadLogsButtonConfig.labelText = 'Load Logs';
    this.reloadLogsButtonConfig.disabled = false;

    this.getLogFileButtonConfig.labelText = 'Download Logs';
    this.getLogFileButtonConfig.disabled = false;
  }

  clearConsole(): void {
    this.store.dispatch(ConsoleActions.clearConsoleEntries());
  }

  reloadLogs(): void {
    this.store.dispatch(ConsoleActions.clearConsoleEntries());
    this.communicationService.send({type: 'cmd', command: 'getlogs'});
  }

  getLogFile(): void {
    this.communicationService.send({type: 'cmd', command: 'getlogfile'});
  }
}
