export type DropdownItemValueType = string | number | boolean;

export interface DropdownItem {
  description: string;
  value: DropdownItemValueType;
}

export class DropdownConfiguration {
  labelText: string;
  disabled: boolean;
  closed: boolean;
  items: Array<DropdownItem>;
  selectedIndex: number;
  value: DropdownItemValueType;
  constructor() {
    this.labelText = '';
    this.disabled = false;
    this.closed = true;
    this.items = [];
    this.selectedIndex = -1;
    this.value = undefined;
  }

  initDropdown(labelText: string, disabled: boolean, items: Array<DropdownItem>, selectedIndex: number): void {
    this.labelText = labelText;
    this.disabled = disabled;
    this.items = items;
    this.selectedIndex = selectedIndex;
    this.value = items[selectedIndex]?.value;
  }
}