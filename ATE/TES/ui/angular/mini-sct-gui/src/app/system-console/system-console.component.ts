import { Component, OnInit } from '@angular/core';
import { ButtonConfiguration } from './../basic-ui-elements/button/button-config';
import { AppState } from '../app.state';
import { Store, select } from '@ngrx/store';
import { ConsoleEntry } from '../models/console.model';
import * as ConsoleActions from './../actions/console.actions';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-system-console',
  templateUrl: './system-console.component.html',
  styleUrls: ['./system-console.component.scss']
})
export class SystemConsoleComponent implements OnInit {
  clearConsoleButtonConfig: ButtonConfiguration;

  consoleEntries$: Observable<ConsoleEntry[]>;

  constructor(private readonly store: Store<AppState>) {
    this.clearConsoleButtonConfig = new ButtonConfiguration();
    this.consoleEntries$ = store.pipe(select('consoleEntries'));
  }

  ngOnInit() {
    this.clearConsoleButtonConfig.labelText = 'Clear';
    this.clearConsoleButtonConfig.disabled = false;
  }

  clearConsole() {
    this.store.dispatch(new ConsoleActions.Clear());
  }
}

