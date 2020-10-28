export enum Alignment {
  Center = 'center',
  Left = 'left',
  Right = 'right'
}
export interface TableEntry {
  text: string;
  align: Alignment;
  textColor: string;
  backgroundColor: string;
}

export function generateTableEntry(text: string, align?: Alignment, textColor?: string, backgroundColor?: string): TableEntry {
  return {
    text,
    align,
    textColor,
    backgroundColor
  };
}

export class TableConfiguration {
  headerRow: Array<TableEntry>;
  rows: Array<TableEntry[]>;
  tableWidth: Array<string>;
  constructor() {
    this.headerRow = [];
    this.rows = [];
    this.tableWidth = [];
  }

  initTable(headerRow: Array<TableEntry>, rows: Array<TableEntry[]>, tableWidth?: Array<string>): void {
    this.headerRow = headerRow;
    this.rows = rows;
    this.tableWidth = [];
    if (!tableWidth && this.rows.length > 0) {
      let numberOfColumns = this.rows[0].length;
      const columnWidth = `${100/numberOfColumns}%`;
      for (var i = 0; i < numberOfColumns; ++i) {
        this.tableWidth.push(columnWidth);
      }
    } else {
      if (tableWidth.length === this.rows[0]?.length || tableWidth.length === headerRow?.length) {
        this.tableWidth = tableWidth;
      } else {
        throw new Error('Length of array containing width informations has to be equal to the number of columns');
      }
    }
  }
}
