import { Component, OnInit } from '@angular/core';
import { ButtonConfiguration } from 'src/app/basic-ui-elements/button/button-config';
import { CommunicationService } from 'src/app/services/communication.service';
import { Status, SystemState } from 'src/app/models/status.model';
import { Store } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  title = 'MiniSCT';
  startDutTestButtonConfig: ButtonConfiguration;
  private status: Status;
  private readonly ngUnsubscribe: Subject<void>;

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.startDutTestButtonConfig = new ButtonConfiguration();
    this.ngUnsubscribe = new Subject<void>();
    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( s => this.updateStatus(s));
  }

  ngOnInit() {
    this.startDutTestButtonConfig.labelText = 'Start DUT-Test';
  }

  startDutTest() {
    this.communicationService.send({type: 'cmd', command: 'next'});
  }

  isStartDutTestButtonInvisible(): boolean {
    switch (this.status.state) {
      case SystemState.connecting:
      case SystemState.initialized:
        return true;
    }
    return false;
  }

  private updateButtonConfigs() {
    this.startDutTestButtonConfig.disabled = this.status.state !== SystemState.ready;
    this.startDutTestButtonConfig = Object.assign({}, this.startDutTestButtonConfig);
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateButtonConfigs();
  }
}
