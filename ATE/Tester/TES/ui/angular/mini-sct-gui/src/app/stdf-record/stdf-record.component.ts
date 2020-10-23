import { Component, OnInit, Input } from '@angular/core';
import { StdfRecord, StdfRecordType, getStdfRecordDescription } from 'src/app/stdf/stdf-stuff';
import { initMultichoiceEntry, MultichoiceConfiguration, MultichoiceEntry } from '../basic-ui-elements/multichoice/multichoice-config';

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

  computeMultichoiceConfigurationForTestFlagValue(testFlag: number): MultichoiceConfiguration {
    let bitEncoding = [...Array(8)].map( (x , i )=> (testFlag >> i ) & 1 );
    let label = `TEST_FLG: ${bitEncoding.reverse().toString()}`;
    let readonly = false;
    let items = new Array<MultichoiceEntry>();

    for (let idx = 0; idx < bitEncoding.length; idx++) {
      items.push(
        initMultichoiceEntry(
          this.getTestflagBitDescription(idx),
          bitEncoding[idx] !== 0,
          bitEncoding[idx] === 0?'#0AC473':'#BD2217',
          '#0046AD')
      );
    }

    return {
      readonly,
      items,
      label
    };
  }

  private getTestflagBitDescription(bitPosition: number): string {
    switch(bitPosition) {
      case 0:
        return 'Alarm';
      case 1:
        return 'Result field valid';
      case 2:
        return 'Test is reliable';
      case 3:
        return 'Timeout';
      case 4:
        return 'Test was executed';
      case 5:
        return 'Test aborted';
      case 6:
        return 'Pass/fail flag is valid';
      case 7:
        return 'Test passed';
      default:
        return 'unknown';
    }
  }
}
