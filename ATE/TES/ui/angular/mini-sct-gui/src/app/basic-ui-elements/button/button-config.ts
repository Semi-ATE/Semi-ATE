export class ButtonConfiguration {
  backgroundColor: string;
  textColor: string;
  labelText: string;
  disabled: boolean;
  constructor() {
    this.backgroundColor = '#0046AD';
    this.textColor = 'white';
    this.labelText =  '';
    this.disabled =  true;
  }

  initButton(labelText: string, disabled: boolean): void {
    this.labelText = labelText;
    this.disabled = disabled;
  }
}
