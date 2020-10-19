import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { TabConfiguration } from './tab-config';

@Component({
  selector: 'app-tab',
  templateUrl: './tab.component.html',
  styleUrls: ['./tab.component.scss']
})
export class TabComponent implements OnInit {

  @Input() tabConfig: TabConfiguration;
  @Output() tabChangeEvent: EventEmitter<void>;

  constructor() {
    this.tabConfig = new TabConfiguration();
    this.tabChangeEvent = new EventEmitter<void>();
  }

  ngOnInit(): void {
  }

  selectTab(selectedTabIndex: number) {
    if (this.tabConfig.disabled[selectedTabIndex]) {
      return;
    }
    if (selectedTabIndex !== this.tabConfig.selectedIndex) {
      this.tabConfig.selectedIndex = selectedTabIndex;
      this.tabChangeEvent.emit();
    }
  }
}
