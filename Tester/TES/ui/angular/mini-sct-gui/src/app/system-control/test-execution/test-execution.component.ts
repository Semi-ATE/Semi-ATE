import { Component, OnInit, OnDestroy } from '@angular/core';
import { ButtonConfiguration } from 'src/app/basic-ui-elements/button/button-config';
import { CardConfiguration, CardStyle } from './../../basic-ui-elements/card/card-config';
import { CommunicationService } from './../../services/communication.service';
import { AppState } from 'src/app/app.state';
import { Status, SystemState } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { Store } from '@ngrx/store';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-test-execution',
  templateUrl: './test-execution.component.html',
  styleUrls: ['./test-execution.component.scss']
})
export class TestExecutionComponent implements OnInit, OnDestroy {
  testExecutionControlCardConfiguration: CardConfiguration;
  startDutTestButtonConfig: ButtonConfiguration;

  private status: Status;
  private readonly ngUnsubscribe: Subject<void>; // needed for unsubscribing an preventing memory leaks

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.testExecutionControlCardConfiguration = new CardConfiguration();
    this.startDutTestButtonConfig = new ButtonConfiguration();
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.startDutTestButtonConfig.labelText = 'Start DUT-Test';
    this.testExecutionControlCardConfiguration.initCard(true,  CardStyle.COLUMN_STYLE, 'Test Execution');
    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(s => this.updateStatus(s));
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateButtonConfigs();
  }

  private updateButtonConfigs() {
    this.startDutTestButtonConfig.disabled = this.status.state !== SystemState.ready;
    this.startDutTestButtonConfig = Object.assign({}, this.startDutTestButtonConfig);
  }

  startDutTest() {
    this.communicationService.send({type: 'cmd', command: 'next'});
  }
}
