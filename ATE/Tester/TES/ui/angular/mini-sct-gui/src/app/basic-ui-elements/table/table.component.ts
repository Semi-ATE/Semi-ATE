import { Component, Input, OnInit } from '@angular/core';
import { TableConfiguration, TableEntry } from './table-config';

@Component({
  selector: 'app-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.scss']
})
export class TableComponent implements OnInit {

  @Input() tableConfig: TableConfiguration;

  constructor() {
    this.tableConfig = new TableConfiguration();
  }

  ngOnInit(): void {
  }

  inputFieldEditable(entry: TableEntry): boolean {
    if (entry.callBack?.editable) {
      return true;
    } else {
      return false;
    }
  }

  onInput(entry: TableEntry, value: string): void {
    entry.text = value;
    if (entry.callBack?.valid(value)) {
      entry.callBack.onUserInput(value);
    }
  }
}
