import { Component, OnDestroy, OnInit } from '@angular/core';
import { ButtonConfiguration } from './../basic-ui-elements/button/button-config';
import { AppState } from '../app.state';
import { Store, select } from '@ngrx/store';
import { ConsoleEntry } from '../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { Observable, Subject } from 'rxjs';
import { CommunicationService } from '../services/communication.service';
import { takeUntil } from 'rxjs/operators';
import { DropdownConfiguration } from '../basic-ui-elements/dropdown/dropdown-config';
import { LogLevel, UserSettings } from '../models/usersettings.model';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';

@Component({
  selector: 'app-system-console',
  templateUrl: './system-console.component.html',
  styleUrls: ['./system-console.component.scss']
})
export class SystemConsoleComponent implements OnInit, OnDestroy {
  systemConsoleCardConfiguration: CardConfiguration;
  clearConsoleButtonConfig: ButtonConfiguration;
  reloadLogsButtonConfig: ButtonConfiguration;
  getLogFileButtonConfig: ButtonConfiguration;
  setLogLevelDropdownConfig: DropdownConfiguration;
  consoleEntries$: Observable<ConsoleEntry[]>;
  ngUnsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>, private readonly communicationService: CommunicationService) {
    this.systemConsoleCardConfiguration = new CardConfiguration();
    this.clearConsoleButtonConfig = new ButtonConfiguration();
    this.reloadLogsButtonConfig = new ButtonConfiguration();
    this.getLogFileButtonConfig = new ButtonConfiguration();
    this.setLogLevelDropdownConfig = new DropdownConfiguration();

    this.consoleEntries$ = store.pipe(select('consoleEntries'));
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.systemConsoleCardConfiguration.cardStyle = CardStyle.COLUMN_STYLE_FOR_COMPONENT;
    this.systemConsoleCardConfiguration.labelText = 'Logging';

    this.clearConsoleButtonConfig.labelText = 'Clear';
    this.clearConsoleButtonConfig.disabled = false;

    this.reloadLogsButtonConfig.labelText = 'Reload';
    this.reloadLogsButtonConfig.disabled = false;

    this.getLogFileButtonConfig.labelText = 'Save';
    this.getLogFileButtonConfig.disabled = false;

    this.initLogLevel();
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
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

  setLogLevel(): void {
    this.communicationService.send({type: 'cmd', command: 'setloglevel', level: this.setLogLevelDropdownConfig.value});
  }

  private initLogLevel() {
    this.setLogLevelDropdownConfig.initDropdown('Loglevel', false, [
      {description:'Debug', value: LogLevel.Debug},
      {description:'Info', value: LogLevel.Info},
      {description:'Warning', value: LogLevel.Warning},
      {description:'Error', value: LogLevel.Error}
    ],2);

    this.store.select('userSettings')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(e => this.updateLogLevel(e));
  }

  private updateLogLevel(settings: UserSettings) {
    let index = this.setLogLevelDropdownConfig.items.findIndex(e => e.value === settings.logLevel);
    if (index >= 0) {
      this.setLogLevelDropdownConfig.selectedIndex = index;
    }
  }
}
