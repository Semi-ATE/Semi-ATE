import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { Subject, Subscription } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppState } from '../app.state';
import { ButtonConfiguration } from '../basic-ui-elements/button/button-config';
import { ConsoleEntry } from '../models/console.model';
import { MenuItem } from '../routing-table';
import { AppstateService } from '../services/appstate.service';

@Component({
  selector: 'app-modal-dialog',
  templateUrl: './modal-dialog.component.html',
  styleUrls: ['./modal-dialog.component.scss']
})
export class ModalDialogComponent implements OnInit, OnDestroy {

  dialogVisible: boolean;
  dialogHeaderText: string;
  dialogBodyText: string;
  closeButton: ButtonConfiguration;
  navigateButton: ButtonConfiguration;
  error: boolean;

  private messageOrderIdToShow: number;
  private showDialogSubscription: Subscription;
  private readonly messageFound$: Subject<void>;

  constructor(
    private readonly appStateService: AppstateService,
    private readonly store: Store<AppState>,
    private readonly router: Router) {
    this.dialogVisible = false;
    this.error = false;
    this.dialogHeaderText = '';
    this.dialogBodyText = '';
    this.messageFound$ = new Subject<void>();
    this.closeButton = new ButtonConfiguration();
    this.navigateButton = new ButtonConfiguration();
  }

  ngOnInit(): void {
    this.closeButton.initButton('Close', false);
    this.navigateButton.initButton('Show Log', false);
    this.showDialogSubscription = this.appStateService.showModalDialog$.subscribe( e => this.waitForMessage(e));
  }

  ngOnDestroy(): void {
    this.showDialogSubscription.unsubscribe();
  }

  closeDialog(): void {
    this.dialogVisible = false;
  }

  navigateToLogdata(): void {
    this.closeDialog();
    this.router.navigateByUrl('/' + MenuItem.Logging, {skipLocationChange: false});
  }

  private waitForMessage(messageId: number): void {
    this.messageOrderIdToShow = messageId;
    this.store.select('consoleEntries')
      .pipe(takeUntil(this.messageFound$))
      .subscribe( e => this.checkMessages(e));
  }

  private checkMessages(entries: ConsoleEntry[]): void {
    const entryToShow = entries.find( e => e.orderMessageId === this.messageOrderIdToShow );
    if (entryToShow) {
      this.messageFound$.next();
      this.messageOrderIdToShow = 0;
      this.showMessage(entryToShow);
    }
  }

  private showMessage(entry: ConsoleEntry): void {
    this.dialogVisible = true;
    if (entry.type.trim().toLowerCase() === 'error') {
      this.error = true;
    } else {
      this.error = false;
    }
    const dateFromEntry = new Date(Date.parse(entry.date.trim()));
    this.dialogHeaderText = `${entry.type.trim()} @ ${dateFromEntry.toLocaleTimeString()} / ${dateFromEntry.toLocaleDateString()}`;
    this.dialogBodyText = `${entry.description.trim()}`;
  }
}
