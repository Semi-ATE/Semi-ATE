export enum CardStyle {
  ROW_STYLE = 'rowStyle',
  COLUMN_STYLE = 'columnStyle',
  ROW_STYLE_FOR_SYSTEM = 'rowStyleForSystemSites'
}

export class CardConfiguration {
  shadow: boolean;
  cardStyle: CardStyle;
  labelText: string;

  constructor() {
    this.shadow = false;
    this.cardStyle = CardStyle.ROW_STYLE;
    this.labelText = '';
  }

  initCard(shadow: boolean, cardStyle: CardStyle, labelText: string): void {
    this.shadow = shadow;
    this.cardStyle = cardStyle;
    this.labelText = labelText;
  }
}
