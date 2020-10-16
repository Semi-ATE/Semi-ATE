export enum InputType {
 text = 'text',
 number = 'number'
}

export class InputConfiguration {
  textColor: string;
  errorColor: string;
  type: InputType;
  placeholder: string;
  disabled: boolean;
  errorMsg: string;
  value: string;
  constructor() {
      this.type = InputType.text;
      this.textColor = 'black';
      this.errorColor = 'red';
      this.placeholder =  '';
      this.disabled = false;
      this.errorMsg = '';
      this.value = '';
  }

  initInput(placeholder: string, disabled: boolean, value: string): void {
    this.placeholder = placeholder;
    this.disabled = disabled;
    this.value = value;
  }
}
