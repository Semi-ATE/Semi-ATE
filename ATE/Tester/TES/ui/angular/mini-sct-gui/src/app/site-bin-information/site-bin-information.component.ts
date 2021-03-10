import { SiteHead, computeSiteHeadFromNumbers, STDF_RECORD_ATTRIBUTES, stdfGetValue, computePassedInformationForPartFlag, PrrRecord } from 'src/app/stdf/stdf-stuff';
import { takeUntil } from 'rxjs/operators';
import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { AppState } from '../app.state';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';

enum passStatusLabelText {
  pass = 'PASSED',
  fail = 'FAILED',
  unknown = '---'
}

@Component({
  selector: 'app-site-bin-information',
  templateUrl: './site-bin-information.component.html',
  styleUrls: ['./site-bin-information.component.scss']
})

export class SiteBinInformationComponent implements OnInit, OnDestroy {

  partId: string;
  passStatus: boolean;
  softBin: number;
  hardBin: number;

  @Input() readonly siteNumber: number;
  @Input() readonly headNumber: number;
  @Input() readonly siteName: string;
  @Input() readonly styleForFooter: boolean;

  ngUnSubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>) {
    this.partId = 'Unknown';
    this.softBin = -1;
    this.hardBin = -1;
    this.ngUnSubscribe = new Subject<void>();
    this.siteNumber = -1;
    this.headNumber = 0;
    this.siteName = '';
    this.styleForFooter = false;
  }

  ngOnInit() {
    this.store.select('results')
      .pipe(takeUntil(this.ngUnSubscribe))
      .subscribe(r => {
        this.updateView(r);
      }
    );
  }
  ngOnDestroy() {
    this.ngUnSubscribe.next();
    this.ngUnSubscribe.complete();
  }

  private updateView(result: Map<SiteHead, PrrRecord>) {
    let key: SiteHead = computeSiteHeadFromNumbers(this.siteNumber, this.headNumber);
    let record: PrrRecord = result.get(key);

    if (record) {
      this.partId = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.PART_ID) as string;
      this.softBin = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.SOFT_BIN) as number;
      this.hardBin = stdfGetValue(record, STDF_RECORD_ATTRIBUTES.HARD_BIN) as number;
      this.passStatus = computePassedInformationForPartFlag(stdfGetValue(record, STDF_RECORD_ATTRIBUTES.PART_FLG) as number);
    } else {
      this.partId = 'Unknown';
      this.softBin = -1;
      this.hardBin = -1;
      this.passStatus = undefined;
    }
  }

  getClass(): string {
    if (this.passStatus === true)
      return 'passStyle';
    if (this.passStatus === false)
      return 'failStyle';
    return 'defaultStyle';
  }

  getPassFailText(): string {
    if (this.passStatus === true)
      return passStatusLabelText.pass;
    if (this.passStatus === false)
      return passStatusLabelText.fail;
    return passStatusLabelText.unknown;
  }
}
