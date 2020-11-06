import { Component, OnInit, OnDestroy } from '@angular/core';
import { CheckboxConfiguration } from 'src/app/basic-ui-elements/checkbox/checkbox-config';
import { Subject } from 'rxjs';
import { SdtfRecordFilter, FilterType } from 'src/app/services/stdf-record-filter-service/stdf-record-filter';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { StorageMap } from '@ngx-pwa/local-storage';
import { Store } from '@ngrx/store';
import { AppState, selectDeviceId } from 'src/app/app.state';
import { StdfRecord, STDF_RESULT_RECORDS, computePassedInformationForTestFlag } from 'src/app/stdf/stdf-stuff';
import { takeUntil } from 'rxjs/operators';
import { SettingType, PassFailFilterSetting } from 'src/app/models/storage.model';
import { STDF_RECORD_ATTRIBUTES } from '../../stdf/stdf-stuff';
import { DropdownConfiguration } from 'src/app/basic-ui-elements/dropdown/dropdown-config';

enum TestResult {
  Pass = 0,
  Fail = 1,
}

@Component({
  selector: 'app-stdf-record-pass-fail-filter',
  templateUrl: './stdf-record-pass-fail-filter.component.html',
  styleUrls: ['./stdf-record-pass-fail-filter.component.scss']
})
export class StdfRecordPassFailFilterComponent implements OnInit, OnDestroy {
  passFailCheckboxConfig: CheckboxConfiguration;
  dropdownConfig: DropdownConfiguration;
  private deviceId: string;
  private readonly unsubscribe: Subject<void>;
  private readonly filter$: Subject<SdtfRecordFilter>;
  private readonly filter: SdtfRecordFilter;

  constructor(private readonly filterService: StdfRecordFilterService, private readonly storage: StorageMap, private readonly store: Store<AppState>) {
    this.passFailCheckboxConfig = new CheckboxConfiguration();
    this.dropdownConfig = new DropdownConfiguration();
    this.deviceId = undefined;
    this.unsubscribe = new Subject<void>();
    this.filter$ = new Subject<SdtfRecordFilter>();
    this.filter = {
      active: false,
      filterFunction: (_e: StdfRecord) => true,
      type: FilterType.PassFail,
      strengthen: false
    };
  }

  ngOnInit(): void {
    this.filterService.registerFilter(this.filter$);
    this.updateFilterAndPublish();
    this.subscribeDeviceId();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  filterChanged(): void {
    this.dropdownConfig.disabled = !this.passFailCheckboxConfig.checked;
    this.updateFilterAndPublish();
    this.saveSettings();
  }

  private updateFilterAndPublish() {
    this.filter.active = this.passFailCheckboxConfig.checked;
    this.filter.filterFunction = (r: StdfRecord) => STDF_RESULT_RECORDS.includes(r.type) &&
      r.values.some( k => k.key === STDF_RECORD_ATTRIBUTES.TEST_FLG && this.testFlagMatchesFilter(k.value as number));
    this.filter.strengthen = false;
    this.filter$.next(this.filter);
  }

  private defaultSettings() {
    this.passFailCheckboxConfig.initCheckBox('Pass/Fail Information', false, false);
    this.dropdownConfig.initDropdown('', true, [{description: 'Fail', value: TestResult.Fail}, {description: 'Pass', value: TestResult.Pass}], 0);
  }

  private testFlagMatchesFilter(testFlag: number): boolean {
    switch(this.dropdownConfig.value) {
      case TestResult.Fail:
        return !computePassedInformationForTestFlag(testFlag);
      case TestResult.Pass:
        return computePassedInformationForTestFlag(testFlag);
    }
  }


  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        this.defaultSettings();
        let passFailFilterSetting = e as PassFailFilterSetting;
        if (passFailFilterSetting && typeof passFailFilterSetting.enabled === 'boolean' && typeof passFailFilterSetting.selectedIndex === 'number') {
          this.passFailCheckboxConfig.checked = passFailFilterSetting.enabled;
          this.dropdownConfig.disabled = !passFailFilterSetting.enabled;
          this.dropdownConfig.selectedIndex = passFailFilterSetting.selectedIndex;
          this.dropdownConfig.value = this.dropdownConfig.items[this.dropdownConfig.selectedIndex].value;
          this.filterChanged();
        }
      });
  }

  private saveSettings() {
    let setting: PassFailFilterSetting = {
      selectedIndex: this.dropdownConfig.selectedIndex,
      enabled: this.passFailCheckboxConfig.checked
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.deviceId}${SettingType.PassFailFilter}`;
  }

  private updateDeviceId(id: string) {
    this.deviceId = id;
    this.restoreSettings();
  }

  private subscribeDeviceId() {
    this.store.select(selectDeviceId)
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( e => {
        this.updateDeviceId(e);
      }
    );
  }
}
