import { MenuItem } from 'src/app/routing-table';
import { Router } from '@angular/router';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { SystemState, Status } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { AppState } from '../app.state';
import { Store, select } from '@ngrx/store';
import { takeUntil } from 'rxjs/operators';
import { SystemStatusComponent } from '../system-status/system-status.component';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.scss']
})
export class MenuComponent implements OnInit, OnDestroy {
  private status: Status;
  private readonly ngUnsubscribe: Subject<void>;
  menuItem: any;

  constructor(private readonly store: Store<AppState>, private readonly router: Router) {
    this.menuItem = MenuItem;
    this.status = {} as Status;
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( s => this.updateStatus(s));
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  isDisabled(menuItem: MenuItem): boolean {
    switch (menuItem) {
      case MenuItem.Info:
      case MenuItem.Logging:
        return false;
      case MenuItem.Results:
        return this.resultsDisabled();
      case MenuItem.Control:
        return this.controlDisabled();
    }
  }

  private updateStatus(status: Status) {
    this.status = status;
  }

  private resultsDisabled(): boolean {
    switch (this.status.state) {
      case SystemState.connecting:
      case SystemState.initialized:
      case SystemState.unloading:
      case SystemState.loading:
        return true;
    }
    return false;
  }

  private controlDisabled(): boolean {
    switch (this.status.state) {
      case SystemState.connecting:
        return true;
    }
    return false;
  }

  isActive(path: string): boolean {
    return this.router.url === '/' + path;
  }
}
