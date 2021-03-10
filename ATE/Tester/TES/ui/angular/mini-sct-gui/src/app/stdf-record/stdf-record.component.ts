import { Component, OnInit, Input } from '@angular/core';
import { StdfRecord, StdfRecordType, getStdfRecordDescription, Stdf, stdfGetValue, STDF_RECORD_ATTRIBUTES, computePassedInformationForTestFlag } from 'src/app/stdf/stdf-stuff';
import { initMultichoiceEntry, MultichoiceConfiguration, MultichoiceEntry } from '../basic-ui-elements/multichoice/multichoice-config';

@Component({
  selector: 'app-stdf-record',
  templateUrl: './stdf-record.component.html',
  styleUrls: ['./stdf-record.component.scss']
})
export class StdfRecordComponent implements OnInit {
  @Input()
  stdfRecord: StdfRecord;

  passOrFailTextColor: string;
  passOrFail: string;
  testFlagBitEncoding: string;

  constructor() {
    this.stdfRecord  = {
      type: StdfRecordType.Unknown,
      values: []
    };
    this.passOrFailTextColor = '#0AC473';
    this.passOrFail = 'P';
    this.testFlagBitEncoding = '0, 0, 0, 0, 0, 0, 0, 0';
  }

  ngOnInit(): void {
  }

  getLongType(): string {
    return getStdfRecordDescription(this.stdfRecord);
  }

  getScaledResult(): string {
    return Stdf.computeScaledResultFromSTDF(this.stdfRecord);
  }

  getScaledLowLimit(): string {
    return Stdf.computeScaledLowLimitFromSTDF(this.stdfRecord);
  }

  getScaledHighLimit(): string {
    return Stdf.computeScaledHighLimitFromSTDF(this.stdfRecord);
  }

  getPassStatus(): string {
    let passStatus = computePassedInformationForTestFlag(stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.TEST_FLG) as number);
    if (passStatus === true) {
      this.passOrFail = 'P';
      this.passOrFailTextColor = '#0AC473';
    } else {
      this.passOrFail = 'F';
      this.passOrFailTextColor = '#BD2217';
    }
    return this.passOrFail;
  }

  getTestNumber(): number {
    let testNumber = stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.TEST_NUM) as number;
    return testNumber;
  }

  getHeadNumber(): number {
    let headNumber = stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.HEAD_NUM) as number;
    return headNumber;
  }

  getSiteNumber(): string {
    let siteNumber = stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.SITE_NUM) as number;
    return this.siteNumberToLetter(siteNumber);
  }

  getTestText(): string {
    let testText = stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.TEST_TXT) as string;
    return testText;
  }

  getTestFlag(): number {
    return stdfGetValue(this.stdfRecord, STDF_RECORD_ATTRIBUTES.TEST_FLG) as number;
  }

  private siteNumberToLetter(siteNumber: number): string {
    let s: string;
    let t: number;
    if(siteNumber === 0) {
      return 'A';
    } else if(siteNumber > 0 && siteNumber < 17) {
      while(siteNumber) {
        t = (siteNumber - 1) % 26;
        s = String.fromCharCode(66 + t);
        siteNumber = (siteNumber - t)/26 | 0;
      }
      return s;
    } else {
      return undefined;
    }
  }

  computeMultichoiceConfigurationForTestFlagValue(testFlag: number): MultichoiceConfiguration {
    let bitEncoding = [...Array(8)].map( (_x , i )=> (testFlag >> i ) & 1 );
    this.testFlagBitEncoding = bitEncoding.reverse().toString();
    let label = 'Test Flag: ';
    let readonly = true;
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
