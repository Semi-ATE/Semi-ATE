import { Component, OnInit, Output, Input, EventEmitter } from '@angular/core';
import { InputConfiguration } from './input-config';

@Component({
  selector: 'app-input',
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss']
})
export class InputComponent implements OnInit {
  @Input() inputConfig: InputConfiguration;
  @Output() inputChangeEvent: EventEmitter<string>;

  constructor() {
    this.inputConfig = new InputConfiguration();
    this.inputChangeEvent = new EventEmitter<string>();
  }

  resetErrorMsg() {
    // reset error message on user input
    this.inputConfig.errorMsg = '';
  }

  ngOnInit() {
  }
}
