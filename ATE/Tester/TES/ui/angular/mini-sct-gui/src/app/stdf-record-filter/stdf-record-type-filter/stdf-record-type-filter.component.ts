import { Component, OnInit, OnDestroy } from '@angular/core';
import { StdfRecordType, StdfRecord, ALL_STDF_RECORD_TYPES } from '../../stdf/stdf-stuff';
import { CheckboxConfiguration } from '../../basic-ui-elements/checkbox/checkbox-config';
import { Subject } from 'rxjs';
import { SdtfRecordFilter, FilterType } from '../../services/stdf-record-filter-service/stdf-record-filter';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { ButtonConfiguration } from '../../basic-ui-elements/button/button-config';
import { StorageMap } from '@ngx-pwa/local-storage';
import { AppState, selectDeviceId } from '../../app.state';
import { Store } from '@ngrx/store';
import { takeUntil } from 'rxjs/operators';
import { RecordTypeFilterSetting, SettingType } from '../../models/storage.model';

@Component({
  selector: 'app-stdf-record-type-filter',
  templateUrl: './stdf-record-type-filter.component.html',
  styleUrls: ['./stdf-record-type-filter.component.scss']
})
export class StdfRecordTypeFilterComponent implements OnInit, OnDestroy {
  recordTypeFilterCheckboxes: CheckboxConfiguration[];
  allRecordsSelectedButtonConfig: ButtonConfiguration;
  noneRecordsSelectedButtonConfig: ButtonConfiguration;
  private selectedRecordTypes: Array<StdfRecordType>;
  private readonly filter$: Subject<SdtfRecordFilter>;
  private readonly filter: SdtfRecordFilter;
  private readonly ngUnSubscribe: Subject<void>;
  private deviceId: string;

  constructor(private readonly filterService: StdfRecordFilterService, private readonly storage: StorageMap, private readonly store: Store<AppState>) {
    this.recordTypeFilterCheckboxes = [];
    this.allRecordsSelectedButtonConfig = new ButtonConfiguration();
    this.noneRecordsSelectedButtonConfig = new ButtonConfiguration();
    this.selectedRecordTypes = [];
    this.filter$ = new Subject<SdtfRecordFilter>();
    this.filter = {
      active: true,
      filterFunction: () => true,
      type: FilterType.RecordType,
      strengthen: false
    };
    this.ngUnSubscribe = new Subject<void>();
    this.deviceId = undefined;
  }

  ngOnInit(): void {
    this.filterService.registerFilter(this.filter$);
    this.initStdfRecordTypeCheckboxes();
    this.allRecordsSelectedButtonConfig.labelText = 'All';
    this.noneRecordsSelectedButtonConfig.labelText = 'None';
    this.subscribeDeviceId();
  }

  ngOnDestroy() {
    this.ngUnSubscribe.next();
    this.ngUnSubscribe.complete();
  }

  recordTypeFilterChanged(checked: boolean, type: StdfRecordType) {
    if (checked) {
      this.selectRecordType(type);
    } else {
      this.deselectRecordType(type);
    }
    this.setDisabledStatusRecordFilterButtons();
    this.updateFilterAndPublish(!checked);
    this.saveSettings();
  }

  selectAllRecords() {
    this.selectRecords(true);
    this.updateFilterAndPublish(false);
    this.saveSettings();
  }

  unselectAllRecords() {
    this.selectRecords(false);
    this.updateFilterAndPublish(true);
    this.saveSettings();
  }

  private initStdfRecordTypeCheckboxes(): void {
    this.recordTypeFilterCheckboxes = ALL_STDF_RECORD_TYPES.map(
      e => {
        let conf = new CheckboxConfiguration();
        conf.initCheckBox(e, true, false);
        return conf;
      }
    );
  }

  private selectRecords(all: boolean) {
    for (let i = 0; i < this.recordTypeFilterCheckboxes.length; i++) {
      this.recordTypeFilterCheckboxes[i].checked = all;
    }
    this.selectedRecordTypes = all? ALL_STDF_RECORD_TYPES:[];
    this.setDisabledStatusRecordFilterButtons();
  }

  private updateFilterAndPublish(filterGetsStronger: boolean) {
    this.filter.filterFunction = (r: StdfRecord) =>
      this.selectedRecordTypes.map(i => i === r.type).reduce( (a,v) => a || v, false);
    this.filter.strengthen = filterGetsStronger;
    this.filter$.next(this.filter);
  }

  private setDisabledStatusRecordFilterButtons() {
    this.allRecordsSelectedButtonConfig.disabled = this.recordTypeFilterCheckboxes.every(e => e.checked );
    this.noneRecordsSelectedButtonConfig.disabled = this.recordTypeFilterCheckboxes.every( e => !e.checked );
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

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        let typeFilterSetting = e as RecordTypeFilterSetting;
        if (!typeFilterSetting || !typeFilterSetting.selectedTypes ) {
          this.selectAllRecords();
        } else {
          this.selectedRecordTypes = typeFilterSetting.selectedTypes;
          this.recordTypeFilterCheckboxes.forEach(r => r.checked = false);
          this.selectedRecordTypes.forEach(s => {
            this.recordTypeFilterCheckboxes.find( c => c.labelText === s).checked = true;
          });
          this.setDisabledStatusRecordFilterButtons();
          this.updateFilterAndPublish(true);
        }
    });
  }

  private saveSettings() {
    let setting: RecordTypeFilterSetting = {
      selectedTypes: this.selectedRecordTypes
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.deviceId}${SettingType.RecordTypeFilter}`;
  }

  private updateDeviceId(id: string) {
    this.deviceId = id;
    this.restoreSettings();
  }

  private subscribeDeviceId() {
    this.store.select(selectDeviceId)
      .pipe(takeUntil(this.ngUnSubscribe))
      .subscribe( e => {
        this.updateDeviceId(e);
      }
    );
  }
}
