import { Component, Input, OnInit } from '@angular/core';
import { TableConfiguration } from './table-config';

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
}
