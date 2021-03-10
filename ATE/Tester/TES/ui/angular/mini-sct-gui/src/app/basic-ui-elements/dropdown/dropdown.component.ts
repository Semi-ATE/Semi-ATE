import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { DropdownConfiguration, DropdownItemValueType } from './dropdown-config';

@Component({
  selector: 'app-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {

  @Input() dropdownConfig: DropdownConfiguration;
  @Output() dropdownChangeEvent: EventEmitter<DropdownItemValueType>;

  constructor() {
    this.dropdownConfig = new DropdownConfiguration();
    this.dropdownChangeEvent = new EventEmitter<DropdownItemValueType>();
  }

  ngOnInit() {
  }

  selectedItem(selectedItemIndex: number) {
    if (this.dropdownConfig.disabled) {
      return;
    }
    if (this.dropdownConfig.closed) {
      this.dropdownConfig.closed = false;
    } else {
      this.dropdownConfig.closed = true;
      if (selectedItemIndex !== this.dropdownConfig.selectedIndex) {
        this.dropdownConfig.selectedIndex = selectedItemIndex;
        this.dropdownConfig.value = this.dropdownConfig.items[this.dropdownConfig.selectedIndex].value;
        this.dropdownChangeEvent.emit(this.dropdownConfig.value);
      }
    }
  }
}
