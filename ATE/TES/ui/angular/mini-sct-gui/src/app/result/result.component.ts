import { CommunicationService } from '../services/communication.service';
import { Component, OnInit } from '@angular/core';
import { CardConfiguration, CardStyle } from '../basic-ui-elements/card/card-config';

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.scss']
})

export class ResultComponent implements OnInit {
  systemSiteCardConfiguration: CardConfiguration;

  constructor() {
    this.systemSiteCardConfiguration = new CardConfiguration();
  }

  ngOnInit() {
    this.systemSiteCardConfiguration.cardStyle = CardStyle.ROW_STYLE_FOR_SYSTEM;
    this.systemSiteCardConfiguration.labelText = 'System Sites';
  }
}
