export class TabConfiguration {
  disabled: Array<boolean>;
  labels: Array<string>;
  selectedIndex: number;
  constructor() {
    this.disabled = [];
    this.labels = [];
    this.selectedIndex = 0;
  }

  initTab(disabled: Array<boolean>, labels: Array<string>, selectedIndex: number): void {
    this.disabled = disabled;
    this.labels = labels;
    this.selectedIndex = selectedIndex;
  }
}
