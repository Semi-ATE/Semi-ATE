import { Component, OnInit, Input } from '@angular/core';

export class CardConfiguration {
  shadow: boolean;
  cardStyle: CardStyle;
  labelText: string;

  constructor() {
    this.shadow = false;
    this.cardStyle = CardStyle.ROW_STYLE;
    this.labelText = '';
  }
}

export enum CardStyle {
  ROW_STYLE = 'rowStyle',
  COLUMN_STYLE = 'columnStyle',
  ROW_STYLE_FOR_SYSTEM = 'rowStyleForSystemSites'
}

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html',
  styleUrls: ['./card.component.scss']
})
export class CardComponent implements OnInit {

  @Input()
  cardConfiguration: CardConfiguration;

  constructor() {
    this.cardConfiguration = new CardConfiguration();
  }

  ngOnInit() {}

}
