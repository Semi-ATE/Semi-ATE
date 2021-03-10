import { Component, OnDestroy, OnInit } from '@angular/core';
import { ButtonConfiguration } from './../basic-ui-elements/button/button-config';
import { AppState, selectDeviceId } from '../app.state';
import { Store} from '@ngrx/store';
import { ConsoleEntry } from '../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { Subject } from 'rxjs';
import { CommunicationService } from '../services/communication.service';
import { takeUntil } from 'rxjs/operators';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';
import { initMultichoiceEntry, MultichoiceConfiguration } from '../basic-ui-elements/multichoice/multichoice-config';
import { StorageMap } from '@ngx-pwa/local-storage';
import { LogLevelFilterSetting, SettingType } from '../models/storage.model';
import { AppstateService } from '../services/appstate.service';

export enum LogLevelString {
  Debug = 'DEBUG',
  Info = 'INFO',
  Warning = 'WARNING',
  Error = 'ERROR'
}
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
  setLogLevelFilterConfig: MultichoiceConfiguration;
  private consoleEntries: ConsoleEntry[];
  filteredEntries: ConsoleEntry[];
  private loglevelFilter: Array<LogLevelString>;
  ngUnsubscribe: Subject<void>;
  private deviceId: string;

  constructor(
    private readonly store: Store<AppState>,
    private readonly communicationService: CommunicationService,
    private readonly storage: StorageMap,
    private readonly appStateService: AppstateService
  ) {
    this.systemConsoleCardConfiguration = new CardConfiguration();
    this.clearConsoleButtonConfig = new ButtonConfiguration();
    this.reloadLogsButtonConfig = new ButtonConfiguration();
    this.getLogFileButtonConfig = new ButtonConfiguration();
    this.setLogLevelFilterConfig = {
      readonly: false,
      items: [],
      label: ''
    };
    this.consoleEntries = [];
    this.filteredEntries = [];
    this.loglevelFilter = [];
    this.ngUnsubscribe = new Subject<void>();
    this.deviceId = undefined;
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

    this.initLogLevelFilter();

    this.store.select('consoleEntries')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( e => this.newConsoleEntries(e));
    this.subscribeDeviceId();
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  clearConsole(): void {
    this.store.dispatch(ConsoleActions.clearConsoleEntries());
  }

  reloadLogs(): void {
    this.appStateService.resetDialogMechanism();
    this.store.dispatch(ConsoleActions.clearConsoleEntries());
    this.communicationService.send({type: 'cmd', command: 'getlogs'});
  }

  getLogFile(): void {
    this.communicationService.send({type: 'cmd', command: 'getlogfile'});
  }

  setLogLevelFilter(): void {
    this.loglevelFilter = this.setLogLevelFilterConfig
      .items.filter(e => e.checked)
      .map(e => e.label.toUpperCase()) as Array<LogLevelString>;
    this.filteredEntries = this.consoleEntries.filter( e => this.passesFilter(e));
    this.saveSettings();
  }

  passesFilter(entry: ConsoleEntry): boolean {
    return (this.loglevelFilter.includes(entry.type.trim().toUpperCase() as LogLevelString));
  }

  private initLogLevelFilter() {
    this.setLogLevelFilterConfig.label = 'Loglevel Filter';
    this.setLogLevelFilterConfig.readonly = false;
    this.setLogLevelFilterConfig.items = [];

    this.setLogLevelFilterConfig.items.push(
     initMultichoiceEntry('Debug', true, '#0046AD', 'white')
    );

    this.setLogLevelFilterConfig.items.push(
      initMultichoiceEntry('Info', true, '#0046AD', 'white')
     );

    this.setLogLevelFilterConfig.items.push(
      initMultichoiceEntry('Warning', true, '#0046AD', 'white')
    );

    this.setLogLevelFilterConfig.items.push(
      initMultichoiceEntry('Error', true, '#0046AD', 'white')
    );

    this.loglevelFilter = [LogLevelString.Info, LogLevelString.Warning, LogLevelString.Debug, LogLevelString.Error];
  }

  private newConsoleEntries(entries: ConsoleEntry[]): void {
    this.consoleEntries = entries;
    this.filteredEntries = this.consoleEntries.filter( e => this.passesFilter(e));
  }

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        let logLevelFilterSetting = e as LogLevelFilterSetting;
        if (logLevelFilterSetting && logLevelFilterSetting.logLevelFilter && typeof logLevelFilterSetting.logLevelFilter.length === 'number') {
          this.loglevelFilter = logLevelFilterSetting.logLevelFilter;
          this.setLogLevelFilterConfig.items = this.setLogLevelFilterConfig.items.map(i => {
            i.checked = false;
            return i;
          });
          this.setLogLevelFilterConfig
            .items.filter(i => this.loglevelFilter.includes(i.label.toUpperCase() as LogLevelString))
            .forEach(i => i.checked = true);
          this.setLogLevelFilter();
        }
      });
  }

  private saveSettings() {
    let setting: LogLevelFilterSetting = {
      logLevelFilter: this.loglevelFilter
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.deviceId}${SettingType.LogLevelFilter}`;
  }

  private updateDeviceId(id: string) {
    this.deviceId = id;
    this.restoreSettings();
  }

  private subscribeDeviceId() {
    this.store.select(selectDeviceId)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( e => {
        this.updateDeviceId(e);
      }
    );
  }
}
