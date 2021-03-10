import { MenuItem } from 'src/app/routing-table';
import { Router } from '@angular/router';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { SystemState, Status } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { AppState } from '../app.state';
import { Store } from '@ngrx/store';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.scss']
})
export class MenuComponent implements OnInit, OnDestroy {
  menuItem: any;
  private status: Status;
  private readonly ngUnsubscribe: Subject<void>;

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
      case MenuItem.Records:
        return this.resultsDisabled();
      case MenuItem.Control:
        return this.controlDisabled();
      case MenuItem.Bin:
        return this.binDisabled();
    }
  }

  isActive(path: string): boolean {
    return this.router.url === '/' + path;
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.navigateToInformationIfNeeded();
  }

  private binDisabled(): boolean {
    switch (this.status.state) {
      case SystemState.connecting:
        return true;
    }
    return false;
  }

  private resultsDisabled(): boolean {
    switch (this.status.state) {
      case SystemState.connecting:
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

  private navigateToInformationIfNeeded() {
    let currentUrl = this.router.url;
    if (currentUrl.includes(MenuItem.Bin) && this.binDisabled()) {
      this.router.navigateByUrl('/' + MenuItem.Info, {skipLocationChange: false});
    } if (currentUrl.includes(MenuItem.Control) && this.controlDisabled()) {
      this.router.navigateByUrl('/' + MenuItem.Info, {skipLocationChange: false});
    } else if (currentUrl.includes(MenuItem.Records) && this.resultsDisabled()) {
      this.router.navigateByUrl('/' + MenuItem.Info, {skipLocationChange: false});
    }
  }
}
