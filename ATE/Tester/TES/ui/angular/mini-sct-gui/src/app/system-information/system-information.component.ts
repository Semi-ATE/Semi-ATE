import { InformationConfiguration } from './../basic-ui-elements/information/information-config';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CardConfiguration, CardStyle } from './../basic-ui-elements/card/card-config';
import { Store } from '@ngrx/store';
import { AppState } from '../app.state';
import { Status, SystemState } from './../models/status.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

export enum systemInformationLabelText {
  systemLabelText = 'System',
  sitesLabelText = 'Number of Sites',
  timeLabelText = 'Time',
  environmentLabelText = 'Environment',
  handlerLabelText = 'Handler',
  lotNumberLabelText = 'Lot Number'
}

@Component({
  selector: 'app-system-information',
  templateUrl: './system-information.component.html',
  styleUrls: ['./system-information.component.scss']
})

export class SystemInformationComponent implements OnInit, OnDestroy {
  informationCardConfiguration: CardConfiguration;
  identifyCardConfiguration: CardConfiguration;
  infoContentCardConfiguration: CardConfiguration;

  systemInformationConfiguration: InformationConfiguration;
  numberOfSitesConfiguration: InformationConfiguration;
  timeInformationConfiguration: InformationConfiguration;
  environmentInformationConfiguration: InformationConfiguration;
  handlerInformationConfiguration: InformationConfiguration;
  lotNumberInformationConfiguration: InformationConfiguration;

  status: Status;
  private readonly ngUnsubscribe: Subject<void>;

  constructor(private readonly store: Store<AppState>) {
    this.informationCardConfiguration = new CardConfiguration();
    this.identifyCardConfiguration = new CardConfiguration();
    this.infoContentCardConfiguration = new CardConfiguration();

    this.systemInformationConfiguration = new InformationConfiguration();
    this.numberOfSitesConfiguration = new InformationConfiguration();
    this.timeInformationConfiguration = new InformationConfiguration();
    this.environmentInformationConfiguration = new InformationConfiguration();
    this.handlerInformationConfiguration = new InformationConfiguration();
    this.lotNumberInformationConfiguration = new InformationConfiguration();
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.informationCardConfiguration.initCard(false, CardStyle.COLUMN_STYLE_FOR_COMPONENT, 'Information');
    this.identifyCardConfiguration.initCard( true, CardStyle.COLUMN_STYLE, 'System Identification');
    this.infoContentCardConfiguration.initCard(true, CardStyle.COLUMN_STYLE, '');

    this.systemInformationConfiguration.labelText = systemInformationLabelText.systemLabelText;
    this.numberOfSitesConfiguration.labelText = systemInformationLabelText.sitesLabelText;
    this.timeInformationConfiguration.labelText = systemInformationLabelText.timeLabelText;
    this.environmentInformationConfiguration.labelText = systemInformationLabelText.environmentLabelText;
    this.handlerInformationConfiguration.labelText = systemInformationLabelText.handlerLabelText;
    this.lotNumberInformationConfiguration.labelText = systemInformationLabelText.lotNumberLabelText;

    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe(s => this.handleSystemStatusUpdate(s));
  }

  private computeTextToDisplay(currentText: string, defaultText: string): string {
    // empty, null or undefined
    if (!currentText)
      return defaultText;
    return currentText;
  }

  private handleSystemStatusUpdate(status: Status) {
    this.status = status;
    this.systemInformationConfiguration.value = this.computeTextToDisplay(this.status.deviceId,'unknown');
    this.numberOfSitesConfiguration.value = this.status.sites.length;
    this.timeInformationConfiguration.value = this.status.time;
    this.environmentInformationConfiguration.value = this.computeTextToDisplay(this.status.env, 'unknown');
    this.handlerInformationConfiguration.value = this.computeTextToDisplay(this.status.handler, 'unknown');
    this.lotNumberInformationConfiguration.value = this.computeTextToDisplay(this.status.lotNumber, 'No lot has been loaded');
  }

  ngOnDestroy() {
    // preventing possible memory leaks
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  isInConnectingState(): boolean {
    return this.status.state === SystemState.connecting;
  }

  showError() {
    return this.status.state === SystemState.error;
  }
}
