import { select, Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import {
  CardConfiguration,
  CardStyle,
} from './../basic-ui-elements/card/card.component';
import { Component, OnInit } from '@angular/core';
import { AppState } from '../app.state';
import { Status } from 'src/app/models/status.model';

@Component({
  selector: 'app-system-bin-status',
  templateUrl: './system-bin-status.component.html',
  styleUrls: ['./system-bin-status.component.scss'],
})
export class SystemBinStatusComponent implements OnInit {
  systemBinStatusCardConfiguration: CardConfiguration;
  siteBinInformationCardConfiguration: CardConfiguration;

  status$: Observable<Status>;

  constructor(private readonly store: Store<AppState>) {
    this.systemBinStatusCardConfiguration = new CardConfiguration();
    this.siteBinInformationCardConfiguration = new CardConfiguration();
    this.status$ = store.pipe(select('systemStatus'));
  }

  ngOnInit() {
    this.systemBinStatusCardConfiguration = {
      shadow: false,
      cardStyle: CardStyle.ROW_STYLE_FOR_SYSTEM,
      labelText: 'System BIN Status',
    };

    this.siteBinInformationCardConfiguration = {
      shadow: true,
      cardStyle: CardStyle.COLUMN_STYLE,
      labelText: '',
    };
  }
}
