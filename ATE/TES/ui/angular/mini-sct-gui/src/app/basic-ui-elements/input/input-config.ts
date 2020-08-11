export enum InputType {
 text = 'text',
 number = 'number'
}

export class InputConfiguration {
  textColor: string;
  type: InputType;
  placeholder: string;
  disabled: boolean;
  errorMsg: string;
  value: string;
  constructor() {
      this.type = InputType.text;
      this.textColor = 'black';
      this.placeholder =  '';
      this.disabled = false;
      this.errorMsg = '';
      this.value = '';
  }
}
