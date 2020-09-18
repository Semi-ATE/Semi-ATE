import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { DropdownConfiguration, DropdownItemValueType } from './dropdown-config';

@Component({
  selector: 'app-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {

  @Input() dropdownConfig: DropdownConfiguration;
  @Output() valueChanged: EventEmitter<void>;

  constructor() {
    this.dropdownConfig = new DropdownConfiguration();
    this.valueChanged = new EventEmitter<void>();
  }

  ngOnInit() {
  }

  dropdownChange(event: Event) {
    this.dropdownConfig.selectedIndex = (event.target as any).selectedIndex;
    this.dropdownConfig.value = this.dropdownConfig.items[this.dropdownConfig.selectedIndex].value;
    this.valueChanged.emit();
  }
}
