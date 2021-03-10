import { Component, OnInit, Output, Input, EventEmitter, OnDestroy } from '@angular/core';
import { Store } from '@ngrx/store';
import { StorageMap } from '@ngx-pwa/local-storage';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppState } from 'src/app/app.state';
import { Status } from 'src/app/models/status.model';
import { InputConfiguration } from './input-config';

const ALLOWED_KEYS = [
  'Enter',
  'Insert',
  'Delete',
  'Backspace',
  'Shift',
  'Control',
  'Alt',
  'Home',
  'End',
  'PageDown',
  'PageUp',
  'ArrowLeft',
  'ArrowUp',
  'ArrowDown',
  'ArrowRight',
];

const MAX_NUMBER_OF_SHOWN_HISTORY_ITEMS = 10;

@Component({
  selector: 'app-input',
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss']
})
export class InputComponent implements OnInit, OnDestroy {
  @Input() inputConfig: InputConfiguration;
  @Output() inputChangeEvent: EventEmitter<void>;
  @Output() carriageReturnEvent: EventEmitter<void>;

  historyVisible: boolean;
  historyItemIndex: number;
  filteredHistory: Array<string>;

  private history: Array<string>;
  private status: Status;
  private readonly unsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>, private readonly storage: StorageMap) {
    this.inputConfig = new InputConfiguration();
    this.inputChangeEvent = new EventEmitter<void>();
    this.carriageReturnEvent = new EventEmitter<void>();
    this.historyVisible = false;
    this.historyItemIndex = -1;
    this.history = [];
    this.filteredHistory = [];
    this.status = undefined;
    this.unsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.subscribeStore();
  }

  ngOnDestroy(): void {
    this.unsubscribe.next();
    this.unsubscribe.complete();
    this.resetErrorMsg();
  }

  onFocus(): void {
    this.resetErrorMsg();
    this.showHistory();
  }

  onBlur(): void {
    this.resetErrorMsg();
  }

  onChange(): void {
    this.inputChangeEvent.emit();
  }

  onKeydown(event: KeyboardEvent): void {
    this.resetErrorMsg();
    if (!ALLOWED_KEYS.includes(event.key)) {
      if (!this.inputConfig.validCharacterRegexp.test(event.key)) {
        event.preventDefault();
      }
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
    }
  }

  onKeyUp(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.onEnter();
    } else {
      if (!['ArrowDown', 'ArrowUp'].includes(event.key)) {
        this.historyItemIndex = -1;
      }

      this.showHistory();

      this.filteredHistory = this.history.filter(e =>
        e.startsWith(this.inputConfig.value) &&
        e !== this.inputConfig.value &&
        this.inputConfig.value !== ''
      ).slice(0, MAX_NUMBER_OF_SHOWN_HISTORY_ITEMS);

      if (this.filteredHistory.length) {
        if (event.key === 'ArrowDown') {
          this.historyItemIndex++;

          if (this.historyItemIndex > this.filteredHistory.length) {
            this.historyItemIndex = 0;
          }
        } else if (event.key === 'ArrowUp') {
          this.historyItemIndex--;

          if (this.historyItemIndex < 0) {
            this.historyItemIndex = this.filteredHistory.length - 1;
          }
        }
      } else {
        this.historyItemIndex = -1;
      }
    }
  }

  getColor(): string {
    if (this.inputConfig.disabled) {
      return 'grey';
    }
    return this.inputConfig.errorMsg !== '' ? this.inputConfig.errorColor : this.inputConfig.textColor;
  }

  onMouseClick(index: number): void {
    this.selectedEntry(index);
    this.hideHistory();
    this.carriageReturnEvent.emit();
  }

  private showHistory(): void {
    this.historyVisible = true;
  }

  private onEnter(): void {
    if (this.historyItemIndex !== -1) {
      this.selectedEntry(this.historyItemIndex);
    } else {
      this.insertToHistory(this.inputConfig.value);
    }
    this.hideHistory();
    this.carriageReturnEvent.emit();
  }

  private resetErrorMsg() {
    if (this.inputConfig.errorMsg) {
      this.popFromHistory();
    }
    this.inputConfig.errorMsg = '';
  }

  private selectedEntry(selectedEntryIndex: number) {
    this.inputConfig.value = this.filteredHistory[selectedEntryIndex];
  }

  private hideHistory(): void {
    this.historyItemIndex = -1;
    this.historyVisible = false;
  }

  private insertToHistory(value: string): void {
    if (!this.history.some(e => e === value)) {
      this.history.push(this.inputConfig.value);
    }
    this.saveSettings();
  }

  private popFromHistory(): void {
    this.history = this.history.slice(0, this.history.length - 1);
    this.saveSettings();
  }

  private restoreSettings() {
    this.storage.get(this.getStorageKey())
      .subscribe(e => this.initDefaultHistory(e as Array<string>));
  }

  private initDefaultHistory(history: Array<string>): void {
    this.history = history ?? [];
  }

  private saveSettings() {
    this.storage.set(this.getStorageKey(), this.history).subscribe(() => { });
  }

  private getStorageKey() {
    return `${this.status.deviceId}${this.inputConfig.autocompleteId}`;
  }

  private updateStatus(status: Status) {
    if (this.status?.deviceId !== status.deviceId) {
      this.status = status;
      this.restoreSettings();
    }
    this.status = status;
  }

  private subscribeStore() {
    this.store.select('systemStatus')
      .pipe(takeUntil(this.unsubscribe))
      .subscribe(s => {
        this.updateStatus(s);
      });
  }
}
