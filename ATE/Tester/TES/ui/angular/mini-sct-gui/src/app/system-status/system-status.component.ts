import { Component, OnInit, OnDestroy } from '@angular/core';
import { SystemState, Status } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { Store } from '@ngrx/store';
import { AppState } from '../app.state';
import { takeUntil } from 'rxjs/operators';

export enum Colors {
  red = 'red',
  yellow = 'yellow',
  green = 'green'
}

class RenderedState {
  description: string;
  value: SystemState;
  color: Colors;

  constructor() {
    this.description = '';
    this.value = SystemState.connecting;
    this.color = Colors.yellow;
  }
}

@Component({
  selector: 'app-system-status',
  templateUrl: './system-status.component.html',
  styleUrls: ['./system-status.component.scss']
})

export class SystemStatusComponent implements OnInit, OnDestroy {

  private readonly states: Array<RenderedState>;
  private status: Status;
  renderedState: RenderedState;
  private readonly ngUnsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>) {
    this.states = [
      {
        description: 'Connecting',
        value: SystemState.connecting,
        color: Colors.yellow
      },
      {
        description : 'Tester initialized',
        value: SystemState.initialized,
        color: Colors.green
      },
      {
        description : 'Loading Test Program',
        value : SystemState.loading,
        color: Colors.yellow
      },
      {
        description : 'Ready for DUT Test',
        value : SystemState.ready,
        color: Colors.green
      },
      {
        description : 'Test Execution',
        value : SystemState.testing,
        color: Colors.red
      },
      {
        description : 'Test paused',
        value : SystemState.paused,
        color: Colors.yellow
      },
      {
        description : 'Unloading Test Program',
        value : SystemState.unloading,
        color: Colors.yellow
      },
      {
        description: 'Error',
        value: SystemState.error,
        color: Colors.red
      },
      {
        description: 'Softerror',
        value: SystemState.softerror,
        color: Colors.red
      },
      {
        description: 'Waiting for Bin-Table',
        value: SystemState.waitingForBinTable,
        color: Colors.yellow
      }
    ];

    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
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
    this.adaptState();
  }

  private adaptState(): void {
    this.renderedState = this.states.filter(s => s.value === this.status.state)[0];
  }
}
