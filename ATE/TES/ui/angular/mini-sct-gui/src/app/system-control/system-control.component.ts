import { CardConfiguration, CardStyle } from 'src/app/basic-ui-elements/card/card.component';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Store } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { Status, SystemState } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-system-control',
  templateUrl: './system-control.component.html',
  styleUrls: ['./system-control.component.scss']
})

export class SystemControlComponent implements OnInit, OnDestroy {

  systemControlCardConfiguration: CardConfiguration;
  private status: Status;
  private ngUnsubscribe: Subject<void>; // needed for unsubscribing an preventing memory leaks

  constructor(private store: Store<AppState>) {
    this.systemControlCardConfiguration = new CardConfiguration();
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.systemControlCardConfiguration.cardStyle = CardStyle.ROW_STYLE;
    this.systemControlCardConfiguration.labelText = 'System Control';
    
    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( s => this.status = s);
  }

  ngOnDestroy() {
    // preventing possible memory leaks
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  renderSystemControlComponent() {
    return this.status.state !== SystemState.error;
  }
}
