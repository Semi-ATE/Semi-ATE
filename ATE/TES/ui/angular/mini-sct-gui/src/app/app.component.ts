import { Component } from '@angular/core';
import { AppstateService} from './services/appstate.service';
import { MockServerService } from './services/mockserver.service';
import * as constants from './services/mockserver-constants';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent {
  constructor(private readonly stateService: AppstateService) {
  }
}

