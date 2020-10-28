import { InputConfiguration, InputType } from './../../basic-ui-elements/input/input-config';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CheckboxConfiguration } from './../../basic-ui-elements/checkbox/checkbox-config';
import { ButtonConfiguration } from 'src/app/basic-ui-elements/button/button-config';
import { CardConfiguration, CardStyle } from 'src/app/basic-ui-elements/card/card-config';
import { CommunicationService } from './../../services/communication.service';
import { Subject } from 'rxjs';
import { Status, SystemState } from 'src/app/models/status.model';
import { Store } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { takeUntil } from 'rxjs/operators';
import { TestOptionType, UserSettings } from 'src/app/models/usersettings.model';

export enum TestOptionLabelText {
  stopOnFail = 'Stop on Fail',
  singleStep = 'Single Step',
  stopAtTestNumber = 'Stop before Test Number',
  triggerForTestNumber = 'Trigger before Test Number',
  triggerOnFailure = 'Trigger On Failure',
  triggerSiteSpecific =  'Trigger Site Specific',

  apply = 'Apply',
  reset = 'Reset'
}

export interface TestOptionValue {
  active: boolean;
  value: number;
}

export class TestOption {
  type: TestOptionType;
  checkboxConfig: CheckboxConfiguration;
  inputConfig: InputConfiguration;
  currentValue: TestOptionValue;
  toBeAppliedValue: TestOptionValue;

  constructor(type: TestOptionType) {
    this.type = type;
    this.checkboxConfig = new CheckboxConfiguration();
    this.inputConfig = new InputConfiguration();
    this.toBeAppliedValue = {active: false, value: -1};
    this.currentValue = {active: false, value: -1};
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
    this.inputConfig.value = this.currentValue.value.toString();
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
  private readonly testOptions: Array<TestOption>;
  private readonly ngUnsubscribe: Subject<void>;

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

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.stopOnFailOption = new TestOption(TestOptionType.stopOnFail);
    this.singleStepOption = new TestOption(TestOptionType.singleStep);
    this.stopAtTestNumberOption = new TestOption(TestOptionType.stopAtTestNumber);
    this.stopAtTestNumberOption.inputConfig.type = InputType.number;
    this.triggerForTestNumberOption = new TestOption(TestOptionType.triggerForTestNumber);
    this.triggerForTestNumberOption.inputConfig.type = InputType.number;
    this.triggerOnFailureOption = new TestOption(TestOptionType.triggerOnFailure);
    this.triggerSiteSpecificOption = new TestOption(TestOptionType.triggerSiteSpecific);
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

    this.testOptionCardConfiguration.initCard(true,  CardStyle.COLUMN_STYLE, 'Options');

    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(s => this.updateStatus(s));

    this.store.select('userSettings')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(e => this.updateTestOptions(e));
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateTestOptionConfigs();
  }

  private updateTestOptions(userSettings: UserSettings) {
    userSettings.testOptions.forEach(e => {
      let option = this.testOptions.find( o => o.type === e.type);
      if (option) {
        option.currentValue = {active: e.value.active, value: e.value.value};
        option.toBeAppliedValue = {active: e.value.active, value: e.value.value};
        option.inputConfig.value = (e.value.value).toString();
        option.checkboxConfig.checked = e.value.active;
      }
    });
    this.applyTestOptionButtonConfig.disabled = true;
    this.resetOptionButtonConfig.disabled = true;
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
    this.testOptions.forEach(o =>
        dataToSend.push({
          name: o.type,
          active: o.toBeAppliedValue.active,
          value: o.toBeAppliedValue.value
        }));
    this.communicationService.send({
      type: 'cmd',
      command: 'usersettings',
      payload: dataToSend
    });
  }

  resetTestOptions() {
    // reset all options
    this.testOptions.forEach(o => { o.reset(); });

    // disable apply and reset button
    this.applyTestOptionButtonConfig.disabled = true;
    this.resetOptionButtonConfig.disabled = true;
  }
}
