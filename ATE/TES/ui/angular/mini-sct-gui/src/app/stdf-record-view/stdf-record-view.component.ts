import { Component, OnInit, OnDestroy } from '@angular/core';
import { AppstateService } from 'src/app/services/appstate.service';
import { CommunicationService } from '../services/communication.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';
import { CheckboxConfiguration } from '../basic-ui-elements/checkbox/checkbox-config';
import { ButtonConfiguration } from '../basic-ui-elements/button/button-config';
import { StdfRecordType, StdfRecord } from '../stdf/stdf-stuff';
import { StdfRecordFilterService } from '../services/stdf-record-filter-service/stdf-record-filter.service';
import { SettingType, RecordViewAutoscrollSetting } from '../models/storage.model';
import { Status } from '../models/status.model';
import { Store } from '@ngrx/store';
import { AppState } from '../app.state';
import { StorageMap } from '@ngx-pwa/local-storage';
import { updateStatus } from '../actions/status.actions';

enum ButtonType {
  PrevButton,
  NextButton
}

enum RecordUpdateType {
  NewRecordsArrived,
  FilterChanged
}

@Component({
  selector: 'app-stdf-record-view',
  templateUrl: './stdf-record-view.component.html',
  styleUrls: ['./stdf-record-view.component.scss']
})
export class StdfRecordViewComponent implements OnInit, OnDestroy {
  stdfRecordsViewCardConfiguration: CardConfiguration;
  autoscrollCheckboxConfig: CheckboxConfiguration;
  previousRecordButtonConfig: ButtonConfiguration;
  nextRecordButtonConfig: ButtonConfiguration;
  refreshButtonConfig: ButtonConfiguration;
  autoScroll: boolean;

  private currentRecordIndex: number;
  private readonly unsubscribe: Subject<void>;
  private status: Status;

  constructor(private readonly communicationService: CommunicationService,
              private readonly filterService: StdfRecordFilterService,
              private readonly appStateService: AppstateService,
              private readonly store: Store<AppState>,
              private readonly storage: StorageMap ) {
    this.initConfigurations();
    this.autoScroll = true;
    this.currentRecordIndex = 0;
    this.unsubscribe = new Subject<void>();
    this.store.select('systemStatus')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe(s => this.status = s);
  }

  ngOnInit(): void {
    this.subscribeFilterService();
    this.stdfRecordsViewCardConfiguration.initCard(false,  CardStyle.ROW_STYLE_FOR_SYSTEM, 'STDF Record View');
    this.initCheckBoxes();
    this.initButtons();
    this.restoreSettings();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
    this.saveSettings();
  }

  currentRecord(): StdfRecord {
    return this.filterService.filteredRecords[this.currentRecordIndex] ??
      {type: StdfRecordType.Unknown, values: []};
  }

  previousRecord(): void {
    if (this.currentRecordIndex > 0) {
      this.currentRecordIndex--;
    }
    this.setDisabledStatusOfButtons();
  }

  nextRecord(): void {
    if (this.currentRecordIndex < this.filterService.filteredRecords.length - 1) {
      this.currentRecordIndex++;
    }
    this.setDisabledStatusOfButtons();
  }

  autoscrollChanged(checked: boolean) {
    if (checked) {
      if (this.filterService.filteredRecords.length === 0)
        this.currentRecordIndex = 0;
      else
        this.currentRecordIndex = this.filterService.filteredRecords.length - 1;
    }
    this.setDisabledStatusOfButtons();
  }

  anyRecordStored(): boolean {
    return this.appStateService.stdfRecords.length > 0;
  }

  filterTooStrong(): boolean {
    return this.anyRecordStored() && this.filterService.filteredRecords.length === 0;
  }

  reloadRecords() {
    this.communicationService.send({type: 'cmd', command: 'getresults'});
  }

  private subscribeFilterService() {
    this.filterService.newResultsAvailable$
      .pipe(takeUntil(this.unsubscribe))
      .subscribe({next: () => this.updateView(RecordUpdateType.NewRecordsArrived)});

    this.filterService.resultChanged$
      .pipe(takeUntil(this.unsubscribe))
      .subscribe({next: () => this.updateView(RecordUpdateType.FilterChanged)});
  }

  private initConfigurations() {
    this.stdfRecordsViewCardConfiguration = new CardConfiguration();
    this.autoscrollCheckboxConfig = new CheckboxConfiguration();
    this.previousRecordButtonConfig = new ButtonConfiguration();
    this.nextRecordButtonConfig = new ButtonConfiguration();
    this.refreshButtonConfig = new ButtonConfiguration();
  }

  private initCheckBoxes() {
    this.autoscrollCheckboxConfig.initCheckBox('Autoscroll', true, false);
  }

  private initButtons() {
    this.previousRecordButtonConfig.labelText = 'prev';
    this.nextRecordButtonConfig.labelText = 'next';
    this.refreshButtonConfig.initButton('Reload Records', false);
  }

  private setDisabledStatusOfButtons() {
    this.previousRecordButtonConfig.disabled = this.buttonDisabled(ButtonType.PrevButton);
    this.nextRecordButtonConfig.disabled = this.buttonDisabled(ButtonType.NextButton);
  }

  private buttonDisabled(buttonType: ButtonType): boolean {
    switch(buttonType) {
      case ButtonType.PrevButton:
        return (this.filterService.filteredRecords.length === 0) || this.currentRecordIndex === 0;
      case ButtonType.NextButton:
        return (this.filterService.filteredRecords.length === 0) || this.currentRecordIndex === (this.filterService.filteredRecords.length - 1);
    }
  }

  private updateView(updateType: RecordUpdateType) {
    switch(updateType) {
      case RecordUpdateType.FilterChanged:
        if (this.filterService.filteredRecords.length !== 0) {
          this.currentRecordIndex = this.filterService.filteredRecords.length - 1;
        }
        break;
      case RecordUpdateType.NewRecordsArrived:
        if (this.filterService.filteredRecords.length !== 0) {
          if (this.autoscrollCheckboxConfig.checked) {
            this.currentRecordIndex = this.filterService.filteredRecords.length - 1;
          }
        }
        break;
      }
    this.setDisabledStatusOfButtons();
  }

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        let autoscrollSetting = e as RecordViewAutoscrollSetting;
        if (autoscrollSetting && typeof autoscrollSetting.enabled === 'boolean') {
          this.autoscrollChanged(autoscrollSetting.enabled);
        } else {
          this.autoscrollChanged(true);
        }
    });
  }

  private saveSettings() {
    let setting: RecordViewAutoscrollSetting = {
      enabled: this.autoscrollCheckboxConfig.checked
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.status.deviceId}${SettingType.RecordViewAutoscroll}`;
  }
}
