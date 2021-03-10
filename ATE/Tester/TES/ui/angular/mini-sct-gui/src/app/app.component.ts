import { Component } from '@angular/core';
import { AppstateService } from './services/appstate.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent {
  constructor(readonly stateService: AppstateService) {
  }
}

