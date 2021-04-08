import { Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { StorageMap } from '@ngx-pwa/local-storage';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppState } from '../app.state';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';
import { TabConfiguration } from '../basic-ui-elements/tab/tab-config';
import { Alignment, generateTableEntry, TableConfiguration } from '../basic-ui-elements/table/table-config';
import { LotData } from '../models/lotdata.model';
import { Status, SystemState } from '../models/status.model';
import { LotDataSetting, SettingType } from '../models/storage.model';
import { STDF_MIR_ATTRIBUTES, MirAttributeDescriptionMap, StdfRecordProperty } from '../stdf/stdf-stuff';

@Component({
  selector: 'app-lot-data',
  templateUrl: './lot-data.component.html',
  styleUrls: ['./lot-data.component.scss']
})
export class LotDataComponent implements OnInit, OnDestroy {
  lotDataCardConfiguration: CardConfiguration;
  lotDataTabConfiguration: TabConfiguration;
  lotDataTableConfiguration: TableConfiguration;

  private lotData: LotData;
  private status: Status;
  private readonly unsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>, private readonly storage: StorageMap) {
    this.lotDataCardConfiguration = new CardConfiguration();
    this.lotDataTabConfiguration = new TabConfiguration();
    this.lotDataTableConfiguration = new TableConfiguration();
    this.lotDataTabConfiguration.labels = ['Important', 'All'];
    this.status = undefined;
    this.lotData = null;
    this.unsubscribe = new Subject<void>();
  }

  ngOnInit(): void {
    this.lotDataCardConfiguration.initCard(true, CardStyle.COLUMN_STYLE, 'Lot Data');

    this.store.select('systemStatus')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( s => {
        this.status = s;
      });

    this.store.select('lotData')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe( l => this.updateLotData(l));

    this.restoreSelectedTabIndex();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  tabChanged(): void {
    this.updateTableElement();
    this.saveSettings();
  }

  showLotData(): boolean {
    switch (this.status.state) {
      case SystemState.ready:
      case SystemState.testing:
        return true;
    }
    return false;
  }

  private updateLotData(data: LotData) {
    this.lotData = data;
    this.updateTableElement();
  }

  private updateTableElement(): void {
    if (this.lotDataTabConfiguration.selectedIndex === 0) {
      this.computeImportantMirTable();
    } else {
      this.computeMirTable();
    }
  }

  private computeImportantMirTable(): void {
    this.lotDataTableConfiguration.headerRow = [];
    this.lotDataTableConfiguration.tableWidth = ['40%', '30%', '30%'];
    this.lotDataTableConfiguration.rows = [
      [
        generateTableEntry(MirAttributeDescriptionMap.LOT_ID + ' / ' + MirAttributeDescriptionMap.SBLOT_ID, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.LOT_ID), {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.SBLOT_ID), {align: Alignment.Right})
      ],
      [
        generateTableEntry(MirAttributeDescriptionMap.MODE_COD, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.MODE_COD), {align: Alignment.Left}),
        generateTableEntry('', {align: Alignment.Right})
      ],
      [
        generateTableEntry(MirAttributeDescriptionMap.USER_TXT, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.USER_TXT), {align: Alignment.Left}),
        generateTableEntry('', {align: Alignment.Right})],
      [
        generateTableEntry(MirAttributeDescriptionMap.TST_TEMP, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.TST_TEMP), {align: Alignment.Left}),
        generateTableEntry('', {align: Alignment.Right})],
      [
        generateTableEntry(MirAttributeDescriptionMap.JOB_NAM, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.JOB_NAM), {align: Alignment.Left}),
        generateTableEntry('', {align: Alignment.Right})],
      [
        generateTableEntry(MirAttributeDescriptionMap.JOB_REV, {align: Alignment.Left}),
        generateTableEntry(this.getMirAttributeValue(STDF_MIR_ATTRIBUTES.JOB_REV), {align: Alignment.Left}),
        generateTableEntry('', {align: Alignment.Right})
      ],
    ];
  }

  private getMirAttributeValue(key: string): string {
    return this.lotData?.values.find(p => p.key === key)?.value.toString() ?? '';
  }

  private computeMirTable() {
    this.lotDataTableConfiguration.headerRow = [
      generateTableEntry('Name', {align: Alignment.Left}),
      generateTableEntry('Wert', {align: Alignment.Left})
    ];
    this.lotDataTableConfiguration.tableWidth = [
      '40%',
      '60%'
    ];
    this.lotDataTableConfiguration.rows = this.lotData?.values.map(
      (e: StdfRecordProperty) => {
        return [
          generateTableEntry(e.key, {align: Alignment.Left}),
          generateTableEntry(e.value.toString(), {align: Alignment.Left}),
        ];
      }
    );
  }

  private restoreSelectedTabIndex() {
    this.lotDataTabConfiguration.selectedIndex = 0;
    this.storage.get(this.getStorageKey())
      .subscribe(e => {
        let lotTabSetting = e as LotDataSetting;
        if(lotTabSetting && typeof lotTabSetting.selectedTabIndex === 'number') {
          this.lotDataTabConfiguration.selectedIndex = lotTabSetting.selectedTabIndex;
          this.tabChanged();
        }
      }
    );
  }

  private saveSettings() {
    let setting: LotDataSetting = {
      selectedTabIndex: this.lotDataTabConfiguration.selectedIndex
    };
    this.storage.set(this.getStorageKey(), setting).subscribe(() => {});
  }

  private getStorageKey() {
    return `${this.status.deviceId}${SettingType.LotData}`;
  }
}
