import { Component, OnInit, Output, Input, EventEmitter } from '@angular/core';
import { InputConfiguration } from './input-config';

const ALLOWED_KEYS = [
  'Enter',
  'Insert',
  'Delete',
  'Backspace',
  'Shift',
  'Control',
  'Alt',
  'Home',
  'End',
  'PageDown',
  'PageUp',
  'ArrowLeft',
  'ArrowUp',
  'ArrowDown',
  'ArrowRight',
];

@Component({
  selector: 'app-input',
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss']
})
export class InputComponent implements OnInit {
  @Input() inputConfig: InputConfiguration;
  @Output() inputChangeEvent: EventEmitter<void>;
  @Output() carriageReturnEvent: EventEmitter<void>;

  constructor() {
    this.inputConfig = new InputConfiguration();
    this.inputChangeEvent = new EventEmitter<void>();
    this.carriageReturnEvent = new EventEmitter<void>();
  }

  resetErrorMsg() {
    this.inputConfig.errorMsg = '';
  }

  ngOnInit() {
  }

  getColor(): string {
    if (this.inputConfig.disabled) {
      return 'grey';
    }
    return this.inputConfig.errorMsg !== ''? this.inputConfig.errorColor:this.inputConfig.textColor;
  }

  onKeydown(event: KeyboardEvent ) {
    if (!ALLOWED_KEYS.includes(event.key)) {
      if (!this.inputConfig.validCharacterRegexp.test(event.key)) {
        event.preventDefault();
      }
    }
  }
}
