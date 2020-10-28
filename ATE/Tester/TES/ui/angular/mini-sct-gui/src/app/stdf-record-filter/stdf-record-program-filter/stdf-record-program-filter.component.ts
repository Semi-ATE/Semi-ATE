import { Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { StorageMap } from '@ngx-pwa/local-storage';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppState, selectDeviceId } from 'src/app/app.state';
import { CheckboxConfiguration } from 'src/app/basic-ui-elements/checkbox/checkbox-config';
import { InputConfiguration } from 'src/app/basic-ui-elements/input/input-config';
import { SettingType, ProgramFilterSetting } from 'src/app/models/storage.model';
import { SdtfRecordProgramFilter } from 'src/app/services/stdf-record-filter-service/stdf-record-filter';
import { StdfRecordFilterService } from 'src/app/services/stdf-record-filter-service/stdf-record-filter.service';
import { computePassedInformationForTestFlag, StdfRecord, STDF_RECORD_ATTRIBUTES, STDF_RESULT_RECORDS } from 'src/app/stdf/stdf-stuff';

export interface TestResult {
  testNumber: number;
  passed: boolean;
}

export interface ProgramPattern {
  pattern: Array<TestResult>;
}

@Component({
  selector: 'app-stdf-record-program-filter',
  templateUrl: './stdf-record-program-filter.component.html',
  styleUrls: ['./stdf-record-program-filter.component.scss']
})
export class StdfRecordProgramFilterComponent implements OnInit, OnDestroy {

  testProgramCheckboxConfig: CheckboxConfiguration;
  testProgramInputConfig: InputConfiguration;
  private deviceId: string;
  private readonly unsubscribe: Subject<void>;
  private readonly filter$: Subject<SdtfRecordProgramFilter>;
  private readonly filter: SdtfRecordProgramFilter;

  constructor(private readonly store: Store<AppState>, private readonly filterService: StdfRecordFilterService, private readonly storage: StorageMap) {
    this.testProgramCheckboxConfig = new CheckboxConfiguration();
    this.testProgramInputConfig = new InputConfiguration();
    this.deviceId = undefined;
    this.unsubscribe = new Subject<void>();
    this.filter$ = new Subject<SdtfRecordProgramFilter>();
    this.filter = {
      active: false,
      filterFunction: () => true
    };
  }

  ngOnInit(): void {
    this.filterService.registerProgramFilter(this.filter$);
    this.updateFilterAndPublish();
    this.subscribeDeviceId();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  testProgramFilterChanged() {
    this.testProgramInputConfig.disabled = !this.testProgramCheckboxConfig.checked;
    this.updateFilterAndPublish();
    this.saveSettings();
    if (!this.testProgramCheckboxConfig.checked) {
      this.testProgramInputConfig.errorMsg = '';
    }
  }

  private updateFilterAndPublish() {
    this.filter.active = this.testProgramCheckboxConfig.checked;
    if (this.testProgramCheckboxConfig.checked) {
      let patterns = this.extractAllPattern(this.testProgramInputConfig.value);
      if (patterns === undefined) {
        this.testProgramInputConfig.errorMsg = 'Input not valid. Valid example: (100,f) && (302,p) || (117,p)';
        return;
      }
      this.testProgramInputConfig.errorMsg = '';
      if (patterns.length === 0)
        this.filter.filterFunction = (_e: StdfRecord[]) => true;
      else
        this.filter.filterFunction =
          (r: StdfRecord[]) => patterns.some(p => p.pattern.every(pr => r.some(t => this.recordMatches(t, pr.testNumber, pr.passed))));
    }
    this.filter$.next(this.filter);
  }

  private recordMatches(s: StdfRecord, testNumber: number, passed: boolean): boolean {
    if (STDF_RESULT_RECORDS.includes(s.type))
      return s.values.some(v => v.key === STDF_RECORD_ATTRIBUTES.TEST_NUM && v.value === testNumber) &&
             s.values.some(v => v.key === STDF_RECORD_ATTRIBUTES.TEST_FLG && computePassedInformationForTestFlag(v.value as number) === passed);
    return false;
  }

  private defaultSettings() {
    this.testProgramCheckboxConfig.initCheckBox('Program Pattern', false, false);
    this.testProgramInputConfig.initInput('Pattern', true, '',/([0-9]|&|\||\(|\)|,|p|f|P|F|\s)/);
  }

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe( e => {
        this.defaultSettings();
        let programFilterSetting = e as ProgramFilterSetting;
        if (programFilterSetting && typeof programFilterSetting.value === 'string' && typeof programFilterSetting.enabled === 'boolean' ) {
          this.testProgramCheckboxConfig.checked = programFilterSetting.enabled;
          this.testProgramInputConfig.disabled = !programFilterSetting.enabled;
          this.testProgramInputConfig.value = programFilterSetting.value;
          this.testProgramFilterChanged();
        }
      });
  }

  private saveSettings() {
    let setting: ProgramFilterSetting = {
      enabled: this.testProgramCheckboxConfig.checked,
      value: this.testProgramInputConfig.value
    };
    this.storage.set(this.getStorageKey(), setting).subscribe( () => {});
  }

  private getStorageKey() {
    return `${this.deviceId}${SettingType.ProgramFilter}`;
  }

  private extractAllPattern(value: string ): Array<ProgramPattern> {
    if (this.inputValid(value)) {
      let result = [];
      value = this.normalizeInput(value);
      let patterns = value.split('||').filter(e => e !== '');
      for (let idx=0; idx < patterns.length; ++idx) {
        let extractedPattern = this.extractPattern(patterns[idx]);
        if (extractedPattern === undefined)
          return undefined;
        if (extractedPattern.pattern.length === 0)
          continue;
        result.push(extractedPattern);
      }
      return result;
    }
    return undefined;
  }

  private extractPattern(value: string): ProgramPattern {
    let result: ProgramPattern;
    value = this.normalizeInput(value);
    let pattern = /^\([0-9]+,[a-z]+\)(&&\([0-9]+,[a-z]+\))*$/;
    if (pattern.test(value)) {
      let testResults = value.split('&&').filter(e => e !== '');
      let programPattern = new Array<TestResult>();
      for (let idx=0; idx < testResults.length; ++idx) {
        let testResult = this.extractTestResult(testResults[idx]);
        if (testResult === undefined)
          return;
        programPattern.push(testResult);
      }
      return {
        pattern: programPattern
      };
    }
    return result;
  }

  private extractTestResult(value: string): TestResult {
    let result: TestResult;
    value = this.normalizeInput(value);
    let pattern = /^\([0-9]+,(f|t|p).*\)$/;
    if (pattern.test(value) ) {
      let noBraces = value.replace(/(\(|\))/g, '');
      let noTruePass = noBraces.replace(/(t.*|p.*)/g, 'p');
      let noFalseFails = noTruePass.replace(/f.*/g, 'f');
      let numberResult = noFalseFails.split(',');
      let testNumber = parseInt(numberResult[0], 10);
      let passed = numberResult[1] === 'p';
      result = {
        testNumber,
        passed
      };
    }
    return result;
  }

  private normalizeInput(value: string): string {
    let lower = value.toLocaleLowerCase();
    let noSpaces = lower.replace(/\s*/g, '');
    return noSpaces;
  }

  private inputValid(value: string): boolean {
    let normalizedValue = this.normalizeInput(value);
    if (normalizedValue === '') {
      return true;
    }
    let dnfRegExp = /^\([0-9]+,(f|t|p).*\)((&&|\|{2})\([0-9]+,(f|t|p).*\))*$/;
    let result = dnfRegExp.test(normalizedValue);
    return result;
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
