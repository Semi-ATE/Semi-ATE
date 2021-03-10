export enum BinType {
  Alarm = 'Alarm',
  Type1 = 'Type 1',
  Type2 = 'Type 2',
  FailElectric = 'Fail Electric',
  FailContact = 'Fail Contact',
}
export interface SiteCount {
  siteId: string;
  count: number;
}
export interface BinTable {
  name: string;
  type: BinType;
  sBin: number;
  hBin: number;
  siteCounts: Array<SiteCount>;
}

export type BinTableData = Array<BinTable>;
