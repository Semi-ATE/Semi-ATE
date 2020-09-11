import { CheckboxConfiguration } from './checkbox-config';
import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-checkbox',
  templateUrl: './checkbox.component.html',
  styleUrls: ['./checkbox.component.scss']
})
export class CheckboxComponent implements OnInit {
  @Input() checkboxConfig: CheckboxConfiguration;
  @Output() checkboxChangeEvent: EventEmitter<boolean>;

  checkboxValueChange(checkboxValue: boolean) {
    this.checkboxChangeEvent.emit(checkboxValue);
  }

  constructor() {
    this.checkboxConfig = new CheckboxConfiguration();
    this.checkboxChangeEvent = new EventEmitter<boolean>();
  }

  ngOnInit() {
  }

}
