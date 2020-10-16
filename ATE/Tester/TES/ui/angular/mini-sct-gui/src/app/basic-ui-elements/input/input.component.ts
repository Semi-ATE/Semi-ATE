import { Component, OnInit, Output, Input, EventEmitter } from '@angular/core';
import { InputConfiguration } from './input-config';
import { getQueryPredicate } from '@angular/compiler/src/render3/view/util';

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
    // reset error message on user input
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
}
