import { Component, OnInit, Input } from '@angular/core';
import { StdfRecord, StdfRecordType, getStdfRecordDescription } from 'src/app/stdf/stdf-stuff';

@Component({
  selector: 'app-stdf-record',
  templateUrl: './stdf-record.component.html',
  styleUrls: ['./stdf-record.component.scss']
})
export class StdfRecordComponent implements OnInit {
  @Input()
  stdfRecord: StdfRecord;

  constructor() {
    this.stdfRecord  = {
      type: StdfRecordType.Unknown,
      values: []
    };
  }

  ngOnInit(): void {
  }

  getLongType(): string {
    return getStdfRecordDescription(this.stdfRecord);
  }
}
