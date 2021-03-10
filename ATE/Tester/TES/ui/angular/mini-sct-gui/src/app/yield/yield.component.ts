import { Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { StorageMap } from '@ngx-pwa/local-storage';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppState } from '../app.state';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';
import { TabConfiguration } from '../basic-ui-elements/tab/tab-config';
import { Alignment, generateTableEntry, TableConfiguration } from '../basic-ui-elements/table/table-config';
import { Status } from '../models/status.model';
import { SettingType, YieldSetting } from '../models/storage.model';
import { YieldData } from '../models/yield.model';
import { getSiteName } from '../stdf/stdf-stuff';

@Component({
  selector: 'app-yield',
  templateUrl: './yield.component.html',
  styleUrls: ['./yield.component.scss']
})
export class YieldComponent implements OnInit, OnDestroy {
  yieldCardConfiguration: CardConfiguration;
  yieldTabConfiguration: TabConfiguration;
  yieldTableConfiguration: TableConfiguration;
  private yieldData: YieldData;
  private status: Status;
  private readonly unsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>, private readonly storage: StorageMap) {
    this.yieldCardConfiguration = new CardConfiguration();
    this.yieldTabConfiguration = new TabConfiguration();
    this.yieldTableConfiguration = new TableConfiguration();
    this.yieldData = [];
    this.status = undefined;
    this.unsubscribe = new Subject<void>();
  }

  ngOnInit(): void {
    this.initElements();
    this.store.select('systemStatus')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( s => this.updateStatus(s));

    this.store.select('yield')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( y => this.updateYieldData(y));

    this.yieldCardConfiguration.initCard(true, CardStyle.COLUMN_STYLE, 'Yield');
    this.restoreSelectedTabIndex();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  tabChanged(): void {
    this.updateYieldTable();
    this.saveSettings();
  }

  yieldDataAvailable(): boolean {
    return this.yieldData.length > 0;
  }

  private computeSiteIdFromSelectedTabIndex(): string {
    return (this.yieldTabConfiguration.selectedIndex === 0) ? '-1': (this.yieldTabConfiguration.selectedIndex - 1).toString();
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateYieldTab();
  }

  private updateYieldTab() {
    let tabLabels = ['Total'];
    for (let i= 0; i < this.status.sites.length; ++i) {
      tabLabels.push(getSiteName(i));
    }
    this.yieldTabConfiguration.labels = tabLabels;
  }

  private updateYieldData(data: YieldData) {
    this.yieldData = data;
    this.updateYieldTable();
  }

  private updateYieldTable(): void {
    let rowsOfInterest = this.yieldData.filter(e => e.siteid === this.computeSiteIdFromSelectedTabIndex());

    this.yieldTableConfiguration.rows = [];
    rowsOfInterest.forEach(e => {
      this.yieldTableConfiguration.rows.push(
        [
          generateTableEntry(e.name),
          generateTableEntry(e.count.toString(), Alignment.Right),
          generateTableEntry(e.name ==='Sum'?'': e.value.toString(), Alignment.Right)]
      );
    });
  }

  private restoreSelectedTabIndex() {
    this.yieldTabConfiguration.selectedIndex = 0;
    this.storage.get(this.getStorageKey())
      .subscribe(e => {
        let yieldSetting = e as YieldSetting;
        if(yieldSetting && typeof yieldSetting.selectedTabIndex === 'number') {
          this.yieldTabConfiguration.selectedIndex = yieldSetting.selectedTabIndex;
          this.tabChanged();
        }
      }
    );
  }

  private initElements() {
    this.yieldTabConfiguration.initTab([false], ['Total'], 0);
    this.yieldTableConfiguration.initTable(
      [generateTableEntry(''), generateTableEntry('Amount', Alignment.Right), generateTableEntry('Percentage', Alignment.Right)],
      [],
      ['40%', '30%', '30%']
    );
  }

  private saveSettings() {
    let setting: YieldSetting = {
      selectedTabIndex: this.yieldTabConfiguration.selectedIndex
    };
    this.storage.set(this.getStorageKey(), setting).subscribe(() => {});
  }

  private getStorageKey() {
    return `${this.status.deviceId}${SettingType.Yield}`;
  }
}
