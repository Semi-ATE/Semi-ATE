import { Component, OnInit, OnDestroy } from '@angular/core';
import { CheckboxConfiguration } from '../../basic-ui-elements/checkbox/checkbox-config';
import { InputConfiguration } from '../../basic-ui-elements/input/input-config';
import { Status } from '../../models/status.model';
import { Subject } from 'rxjs';
import { SdtfRecordFilter, FilterType } from '../../services/stdf-record-filter-service/stdf-record-filter';
import { Store } from '@ngrx/store';
import { AppState } from '../../app.state';
import { StdfRecordFilterService } from '../../services/stdf-record-filter-service/stdf-record-filter.service';
import { StorageMap } from '@ngx-pwa/local-storage';
import { StdfRecord, StdfRecordType, STDF_RESULT_RECORDS, STDF_RECORD_ATTRIBUTES } from '../../stdf/stdf-stuff';
import { takeUntil } from 'rxjs/operators';
import { SettingType, TestTextFilterSetting } from '../../models/storage.model';

@Component({
  selector: 'app-stdf-record-test-text-filter',
  templateUrl: './stdf-record-test-text-filter.component.html',
  styleUrls: ['./stdf-record-test-text-filter.component.scss']
})
export class StdfRecordTestTextFilterComponent implements OnInit, OnDestroy {
  testTextCheckboxConfig: CheckboxConfiguration;
  testTextInputConfig: InputConfiguration;
  private status: Status;
  private readonly unsubscribe: Subject<void>;
  private containedText: string;
  private readonly filter$: Subject<SdtfRecordFilter>;
  private readonly filter: SdtfRecordFilter;

  constructor(private readonly filterService: StdfRecordFilterService, private readonly storage: StorageMap, private readonly store: Store<AppState>) {
    this.testTextCheckboxConfig = new CheckboxConfiguration();
    this.testTextInputConfig = new InputConfiguration();
    this.status = undefined;
    this.unsubscribe = new Subject<void>();
    this.containedText = '';
    this.filter$ = new Subject<SdtfRecordFilter>();
    this.filter = {
      active: false,
      filterFunction: (e: StdfRecord) => true,
      type: FilterType.TestText,
      strengthen: false
    };
  }

  ngOnInit(): void {
    this.store.select('systemStatus')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( s => this.status = s);
    this.filterService.registerFilter(this.filter$);
    this.restoreSettings();
    this.updateFilterAndPublish(false);
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
    this.saveSettings();
  }

  testTextFilterCheckboxChanged(): void {
    this.containedText = this.testTextInputConfig.value;
    this.testTextInputConfig.disabled = !this.testTextCheckboxConfig.checked;
    this.updateFilterAndPublish(false);
  }

  testTextFilterValueChanged(inputValue: string ): void {
    let stronger = inputValue.includes(this.containedText);
    this.containedText = inputValue;
    this.updateFilterAndPublish(stronger);
  }

  private updateFilterAndPublish(filterStronger: boolean) {
    this.filter.active = this.testTextCheckboxConfig.checked;
    this.filter.filterFunction =
      (r: StdfRecord) => STDF_RESULT_RECORDS.includes(r.type) &&
        r.values.some( k => k.key === STDF_RECORD_ATTRIBUTES.TEST_TXT && (k.value as string).includes(this.containedText));
    this.filter.strengthen = filterStronger;
    this.filter$.next(this.filter);
  }

  private defaultSettings() {
    this.containedText = '';
    this.testTextCheckboxConfig.initCheckBox('Value contained in TEST_TXT', false, false);
    this.testTextInputConfig.initInput('Contained text', true, '');
  }

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        this.defaultSettings();
        let testFilterSetting = e as TestTextFilterSetting;
        if (testFilterSetting && typeof testFilterSetting.containedTestText === 'string' && typeof testFilterSetting.enabled === 'boolean' ) {
          this.testTextCheckboxConfig.checked = testFilterSetting.enabled;
          this.testTextInputConfig.disabled = !testFilterSetting.enabled;
          this.testTextInputConfig.value = testFilterSetting.containedTestText;
          this.testTextFilterValueChanged(testFilterSetting.containedTestText);
        }
      });
  }

  private saveSettings() {
    let setting: TestTextFilterSetting = {
      containedTestText: this.testTextInputConfig.value,
      enabled: this.testTextCheckboxConfig.checked
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.status.deviceId}${SettingType.TestTextFilter}`;
  }
}
