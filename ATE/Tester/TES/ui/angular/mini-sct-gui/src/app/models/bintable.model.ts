export interface SiteCount {
  siteId: string;
  count: number;
}
export interface BinTable {
  name: string;
  type: string;
  sBin: number;
  hBin: number;
  siteCounts: Array<SiteCount>;
}

export type BinTableData = Array<BinTable>;
