import { Component, OnInit, OnDestroy } from '@angular/core';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card.component';
import { AppstateService } from 'src/app/services/appstate.service';
import { StdfRecordType, StdfRecord, ALL_STDF_RECORD_TYPES } from '../stdf/stdf-stuff';
import { CheckboxConfiguration } from '../basic-ui-elements/checkbox/checkbox-config';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ButtonConfiguration } from '../basic-ui-elements/button/button-config';
import { CommunicationService } from '../services/communication.service';

enum ButtonType {
  PrevButton,
  NextButton
}

enum ViewType {
  RecordsAvailable,
  NoRecordsAvailableAtAll,
  NoRecordsByCurrentFilterSettings
}

type FilterFunction = (e: StdfRecord) => boolean;

@Component({
  selector: 'app-stdf-record-view',
  templateUrl: './stdf-record-view.component.html',
  styleUrls: ['./stdf-record-view.component.scss']
})
export class StdfRecordViewComponent implements OnInit, OnDestroy {
  stdfRecordsViewCardConfiguration: CardConfiguration;
  recordTypeFilterCheckboxes: CheckboxConfiguration[];
  autoscrollCheckboxConfig: CheckboxConfiguration;
  previousRecordButtonConfig: ButtonConfiguration;
  nextRecordButtonConfig: ButtonConfiguration;
  refreshButtonConfig: ButtonConfiguration;

  currentRecordIndex: number;
  disabled: boolean;
  autoScroll: boolean;
  private readonly unsubscribe: Subject<void>;
  private selectedRecordTypes: Array<StdfRecordType>;
  filteredRecords: StdfRecord[];

  constructor(private readonly appStateService: AppstateService, private readonly communicationService: CommunicationService ) {
    this.filteredRecords = [];
    this.stdfRecordsViewCardConfiguration = new CardConfiguration();
    this.currentRecordIndex = 0;
    this.autoScroll = true;
    this.selectedRecordTypes = ALL_STDF_RECORD_TYPES;
    this.recordTypeFilterCheckboxes = [];
    this.previousRecordButtonConfig = new ButtonConfiguration();
    this.nextRecordButtonConfig = new ButtonConfiguration();
    this.refreshButtonConfig = new ButtonConfiguration();
    this.unsubscribe = new Subject<void>();
  }

  ngOnInit(): void {
    this.stdfRecordsViewCardConfiguration = {
      shadow: false,
      cardStyle: CardStyle.ROW_STYLE_FOR_SYSTEM,
      labelText: 'STDF Record View',
    };
    this.recordTypeFilterCheckboxes = ALL_STDF_RECORD_TYPES.map(
      e => {
        let conf = new CheckboxConfiguration();
        conf.labelText = e;
        conf.checked = true;
        conf.disabled = false;
        return conf;
      });
    this.autoscrollCheckboxConfig = {
      labelText: 'Autoscroll',
      checked: true,
      disabled: false
    };
    this.previousRecordButtonConfig.labelText = 'prev';
    this.nextRecordButtonConfig.labelText = 'next';
    this.refreshButtonConfig.labelText = 'Reload Records';
    this.refreshButtonConfig.disabled = false;
    this.setDisabledStatusOfButtons();

    this.appStateService.newRecordReceived$
      .pipe(takeUntil(this.unsubscribe))
      .subscribe({next: (newRecords: StdfRecord[]) => this.updateView(newRecords)});

    this.appStateService.rebuildRecords$
      .pipe(takeUntil(this.unsubscribe))
      .subscribe({next: () => this.applyFilters(false)});

    this.applyFilters(false);
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  currentRecord() {
    return this.filteredRecords?.[this.currentRecordIndex] ??
      {type: StdfRecordType.Unknown, values: []};
  }

  previousRecord(): void {
    if (this.currentRecordIndex > 0) {
      this.currentRecordIndex--;
    }
    this.setDisabledStatusOfButtons();
  }

  nextRecord(): void {
    if (this.currentRecordIndex < this.filteredRecords.length - 1) {
      this.currentRecordIndex++;
    }
    this.setDisabledStatusOfButtons();
  }

  autoscrollChanged(checked: boolean) {
    this.autoScroll = checked;
    if (checked) {
      this.currentRecordIndex = this.filteredRecords.length - 1;
    }
    this.setDisabledStatusOfButtons();
  }

  recordTypeFilterChanged(checked: boolean, type: StdfRecordType) {
    if (checked) {
      this.selectRecordType(type);
    } else {
      this.deselectRecordType(type);
    }
    // compute filteredRecords
    this.applyFilters(!checked);
  }

  anyRecordStored(): boolean {
    switch(this.computeViewType()) {
      case ViewType.NoRecordsAvailableAtAll:
        return false;
      case ViewType.RecordsAvailable:
      case ViewType.NoRecordsByCurrentFilterSettings:
        return true;
    }
  }

  filterTooStrong(): boolean {
    return this.computeViewType() === ViewType.NoRecordsByCurrentFilterSettings;
  }

  reloadRecords() {
    this.communicationService.send({type: 'cmd', command: 'getresults'});
  }

  private setDisabledStatusOfButtons() {
    this.previousRecordButtonConfig.disabled = this.buttonDisabled(ButtonType.PrevButton);
    this.nextRecordButtonConfig.disabled = this.buttonDisabled(ButtonType.NextButton);
  }

  private buttonDisabled(buttonType: ButtonType): boolean {
    switch(buttonType) {
      case ButtonType.PrevButton:
        return (this.filteredRecords.length === 0) || this.currentRecordIndex === 0;
      case ButtonType.NextButton:
        return (this.filteredRecords.length === 0) || this.currentRecordIndex === (this.filteredRecords.length - 1);
    }
  }

  private applyFilters(filterAdded: boolean) {
    // in case that some filter is added it is sufficient to filter
    // the filteredRecords array
    if (filterAdded) {
      this.filteredRecords = (this.filteredRecords ?? []).filter(this.allFilters());
    } else {
      this.filteredRecords = (this.appStateService.stdfRecords ?? []).filter(this.allFilters());
    }
    this.currentRecordIndex = this.filteredRecords.length - 1;
    this.setDisabledStatusOfButtons();
    this.computeViewType();
  }

  private updateView(newRecords: StdfRecord[]) {
    // filter new records
    let filteredNewRecords = newRecords.filter(this.allFilters());
    this.filteredRecords = this.filteredRecords.concat(filteredNewRecords);
    if (this.filteredRecords.length !== 0) {
      if (this.autoScroll) {
        this.currentRecordIndex = this.filteredRecords.length - 1;
      }
    }
    this.setDisabledStatusOfButtons();
    this.computeViewType();
  }

  private selectRecordType(type: StdfRecordType) {
    if (this.typeSelected(type))
      return;
    this.selectedRecordTypes.push(type);
  }

  private typeSelected(type: StdfRecordType): boolean {
    return this.selectedRecordTypes.some(e => e === type);
  }

  private deselectRecordType(type: StdfRecordType) {
    if (!this.typeSelected(type))
      return;
    this.selectedRecordTypes = this.selectedRecordTypes.filter(e => e !==type);
  }

  private allFilters(): FilterFunction {
    let allFilters = [
      this.recordTypeFilter(),
      this.siteFilter(),
      this.testNumberFilter(),
      this.passFailFilter(),
      this.testTextFilter()
    ];
    return allFilters.reduce( (a,f) => (r:StdfRecord) => a(r) && f(r));
  }

  private recordTypeFilter(): FilterFunction {
    return (r: StdfRecord) =>
      this.selectedRecordTypes.map(i => i === r.type).reduce( (a,v) => a || v, false);
  }

  private siteFilter(): FilterFunction {
    return (r: StdfRecord) => true;
  }

  private testNumberFilter(): FilterFunction {
    return (r: StdfRecord) => true;
  }

  private passFailFilter(): FilterFunction {
    return (r: StdfRecord) => true;
  }

  private testTextFilter(): FilterFunction {
    return (r: StdfRecord) => true;
  }

  private computeViewType(): ViewType {
    if (this.appStateService.stdfRecords.length === 0)
      return ViewType.NoRecordsAvailableAtAll;

    if (this.filteredRecords.length === 0 )
      return ViewType.NoRecordsByCurrentFilterSettings;

    return ViewType.RecordsAvailable;
  }
}
