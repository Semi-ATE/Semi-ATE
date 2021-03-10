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
  validCharacterRegexp: RegExp;
  autocompleteId: string;
  constructor() {
    this.type = InputType.text;
    this.textColor = 'black';
    this.errorColor = 'red';
    this.placeholder = '';
    this.disabled = false;
    this.errorMsg = '';
    this.value = '';
    this.validCharacterRegexp = /./;
    this.autocompleteId = '';
  }

  initInput(placeholder: string, disabled: boolean, value: string, validCharacterRegexp: RegExp = /./, autocompleteId: string = ''): void {
    this.placeholder = placeholder;
    this.disabled = disabled;
    this.value = value;
    this.validCharacterRegexp = validCharacterRegexp;
    this.autocompleteId = autocompleteId;
  }
}
