export class CheckboxConfiguration {
  labelText: string;
  checked: boolean;
  disabled: boolean;
  constructor() {
    this.labelText = '';
    this.checked = false;
    this.disabled = false;
  }

  initCheckBox(labelText: string, checked: boolean, disabled: boolean): void {
    this.labelText = labelText;
    this.checked = checked;
    this.disabled = disabled;
  }
}
