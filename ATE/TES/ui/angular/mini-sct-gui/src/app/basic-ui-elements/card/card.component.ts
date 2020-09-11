import { Component, OnInit, Input } from '@angular/core';
import { CardConfiguration } from './card-config';

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
