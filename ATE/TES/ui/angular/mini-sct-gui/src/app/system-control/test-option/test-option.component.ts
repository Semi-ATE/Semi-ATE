import { InputConfiguration } from './../../basic-ui-elements/input/input-config';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CheckboxConfiguration } from './../../basic-ui-elements/checkbox/checkbox-config';
import { ButtonConfiguration } from 'src/app/basic-ui-elements/button/button-config';
import { CardConfiguration, CardStyle } from 'src/app/basic-ui-elements/card/card.component';
import { CommunicationService } from './../../services/communication.service';
import { Subject } from 'rxjs';
import { Status, SystemState } from 'src/app/models/status.model';
import { Store } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { takeUntil } from 'rxjs/operators';

export enum TestOptionLabelText {
  stopOnFail = 'Stop on Fail',
  singleStep = 'Single Step',
  stopAtTestNumber = 'Stop at Test Number',
  triggerForTestNumber = 'Trigger For Test Number',
  triggerOnFailure = 'Trigger On Failure',
  triggerSiteSpecific =  'Trigger Site Specific',

  apply = 'Apply',
  reset = 'Reset'
}

export class TestOptionValue {
  active: boolean;
  value: string;

  constructor() {
    this.active = false;
    this.value = '';
  }
}

export class TestOption {
  name: string;
  checkboxConfig: CheckboxConfiguration;
  inputConfig: InputConfiguration;
  currentValue: TestOptionValue;
  toBeAppliedValue: TestOptionValue;

  constructor(name: string) {
    this.name = name;
    this.checkboxConfig = new CheckboxConfiguration();
    this.inputConfig = new InputConfiguration();
    this.toBeAppliedValue = new TestOptionValue();
    this.currentValue = new TestOptionValue();
  }

  onChange(checked: boolean): void {
    this.toBeAppliedValue.active = checked;
    this.inputConfig.disabled = !this.toBeAppliedValue.active;
  }

  haveToApply(): boolean {
    let anyChanges = this.toBeAppliedValue.active !== this.currentValue.active;
    anyChanges = anyChanges || this.toBeAppliedValue.value !== this.currentValue.value;
    return anyChanges;
  }

  reset(): void {
    this.toBeAppliedValue = Object.assign({}, this.currentValue);
    this.checkboxConfig.checked = this.currentValue.active;
    this.inputConfig.value = this.currentValue.value;
    this.inputConfig.disabled = !this.currentValue.active;
  }
}

@Component({
  selector: 'app-test-option',
  templateUrl: './test-option.component.html',
  styleUrls: ['./test-option.component.scss']
})
export class TestOptionComponent implements OnInit, OnDestroy {

  private status: Status;
  private testOptions: Array<TestOption>;
  private ngUnsubscribe: Subject<void>;

  // Test options
  stopOnFailOption: TestOption;
  singleStepOption: TestOption;
  stopAtTestNumberOption: TestOption;
  triggerForTestNumberOption: TestOption;
  triggerOnFailureOption: TestOption;
  triggerSiteSpecificOption: TestOption;
  testOptionCardConfiguration: CardConfiguration;
  applyTestOptionButtonConfig: ButtonConfiguration;
  resetOptionButtonConfig: ButtonConfiguration;

  constructor(private readonly communicationService: CommunicationService, private store: Store<AppState>) {
    this.stopOnFailOption = new TestOption('stop_on_fail');
    this.singleStepOption = new TestOption('single_step');
    this.stopAtTestNumberOption = new TestOption('stop_at_test_number');
    this.triggerForTestNumberOption = new TestOption('trigger_for_test_number');
    this.triggerOnFailureOption = new TestOption('trigger_on_failure');
    this.triggerSiteSpecificOption = new TestOption('trigger_site_specific');
    this.testOptionCardConfiguration = new CardConfiguration();
    this.applyTestOptionButtonConfig = new ButtonConfiguration();
    this.resetOptionButtonConfig = new ButtonConfiguration();
    this.testOptions = [
      this.stopOnFailOption,
      this.singleStepOption,
      this.stopAtTestNumberOption,
      this.triggerForTestNumberOption,
      this.triggerOnFailureOption,
      this.triggerSiteSpecificOption
    ];
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.stopOnFailOption.checkboxConfig.labelText = TestOptionLabelText.stopOnFail;
    this.singleStepOption.checkboxConfig.labelText = TestOptionLabelText.singleStep;
    this.triggerOnFailureOption.checkboxConfig.labelText = TestOptionLabelText.triggerOnFailure;
    this.triggerSiteSpecificOption.checkboxConfig.labelText = TestOptionLabelText.triggerSiteSpecific;

    this.stopAtTestNumberOption.checkboxConfig.labelText = TestOptionLabelText.stopAtTestNumber;
    this.stopAtTestNumberOption.inputConfig.placeholder = 'Enter test number';
    this.triggerForTestNumberOption.checkboxConfig.labelText = TestOptionLabelText.triggerForTestNumber;
    this.triggerForTestNumberOption.inputConfig.placeholder = 'Enter test number';

    this.applyTestOptionButtonConfig.labelText = TestOptionLabelText.apply;
    this.applyTestOptionButtonConfig.disabled = true;

    this.resetOptionButtonConfig.labelText = TestOptionLabelText.reset;

    this.testOptionCardConfiguration = {
      shadow: true,
      cardStyle: CardStyle.COLUMN_STYLE,
      labelText: 'Options'
    };

    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(s => this.updateStatus(s));
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateTestOptionConfigs();
  }

  private updateTestOptionConfigs() {
    this.testOptions.forEach(o => {
      o.checkboxConfig.disabled = this.status.state !== SystemState.ready;
    });
    if (this.status.state !== SystemState.ready) {
      this.stopAtTestNumberOption.inputConfig.disabled = true;
      this.triggerForTestNumberOption.inputConfig.disabled = true;
      this.resetTestOptions();
    }
  }

  optionChanged(checkboxValue: boolean, testOption: TestOption) {
    testOption.onChange(checkboxValue);
    this.applyTestOptionButtonConfig.disabled = !this.anyOptionChanged();
    this.resetOptionButtonConfig.disabled = this.applyTestOptionButtonConfig.disabled;

    this.applyTestOptionButtonConfig = Object.assign({}, this.applyTestOptionButtonConfig);
    this.resetOptionButtonConfig = Object.assign({}, this.resetOptionButtonConfig);
  }

  anyOptionChanged(): boolean {
    let result = false;

    this.testOptions.forEach(o => {
      result = result || o.haveToApply();
    });
    return result;
  }

  sendOptionsToServer(): void {
    let dataToSend = [];
    this.testOptions.forEach(o => {
      if (o.haveToApply()) {
        dataToSend.push({
          name : o.name,
          active : o.toBeAppliedValue.active,
          value : o.toBeAppliedValue.value || ''
        });
      }
    });
    this.communicationService.send(JSON.stringify(dataToSend));
  }

  resetTestOptions() {
    // reset all options
    this.testOptions.forEach(o => { o.reset(); });

    // disable apply and reset button
    this.applyTestOptionButtonConfig.disabled = true;
    this.resetOptionButtonConfig.disabled = true;
  }
}
