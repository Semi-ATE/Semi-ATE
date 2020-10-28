import { Component, OnInit, Output, Input, EventEmitter } from '@angular/core';
import { ButtonConfiguration } from './button-config';

@Component({
  selector: 'app-button',
  templateUrl: './button.component.html',
  styleUrls: ['./button.component.scss']
})

export class ButtonComponent implements OnInit {
  @Input() buttonConfig: ButtonConfiguration;
  @Output() buttonClickEvent: EventEmitter<boolean>;

  onClickButton() {
    this.buttonClickEvent.emit(true);
  }

  constructor() {
    this.buttonConfig = new ButtonConfiguration();
    this.buttonClickEvent = new EventEmitter<boolean>();
  }

  ngOnInit() {}
}
