import { Component, OnInit, OnDestroy } from '@angular/core';
import { ButtonConfiguration } from 'src/app/basic-ui-elements/button/button-config';
import { CardConfiguration, CardStyle } from './../../basic-ui-elements/card/card.component';
import { InputConfiguration } from './../../basic-ui-elements/input/input-config';
import { CommunicationService } from './../../services/communication.service';
import { Status, SystemState } from 'src/app/models/status.model';
import { Subject } from 'rxjs';
import { Store } from '@ngrx/store';
import { AppState } from 'src/app/app.state';
import { takeUntil } from 'rxjs/operators';

enum ButtonTextLabel {
  LoadLot = 'Load Lot',
  UnloadLot = 'Unload Lot'
}

@Component({
  selector: 'app-lot-handling',
  templateUrl: './lot-handling.component.html',
  styleUrls: ['./lot-handling.component.scss']
})
export class LotHandlingComponent implements OnInit, OnDestroy {
  lotCardConfiguration: CardConfiguration;
  lotNumberInputConfig: InputConfiguration;
  loadLotButtonConfig: ButtonConfiguration;
  unloadLotButtonConfig: ButtonConfiguration;

  private status: Status;
  private ngUnsubscribe: Subject<void>; // needed for unsubscribing an preventing memory leaks

  constructor(private readonly communicationService: CommunicationService, private readonly store: Store<AppState>) {
    this.lotCardConfiguration = new CardConfiguration();
    this.lotNumberInputConfig = new InputConfiguration();
    this.loadLotButtonConfig = new ButtonConfiguration();
    this.unloadLotButtonConfig = new ButtonConfiguration();
    this.ngUnsubscribe = new Subject<void>();
  }

  ngOnInit() {
    this.loadLotButtonConfig.labelText = ButtonTextLabel.LoadLot;
    this.unloadLotButtonConfig.labelText = ButtonTextLabel.UnloadLot;
    this.lotNumberInputConfig.placeholder = 'Enter Lot Number';
    this.lotCardConfiguration = {
      shadow: true,
      cardStyle: CardStyle.COLUMN_STYLE,
      labelText: 'Lot Handling'
    };

    this.store.select('systemStatus')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( s => this.updateStatus(s));

    this.updateButtonConfigs();
    this.updateInputConfigs();
  }

  ngOnDestroy() {
    // preventing possible memory leaks
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  loadLot() {
    let errorMsg = {errorText: ''};
    if (this.validateLotNumber(errorMsg)) {
      this.communicationService.send(
        {
          type: 'cmd',
          command: 'load',
          lot_number: this.lotNumberInputConfig.value
      });
    } else {
      this.lotNumberInputConfig.errorMsg = errorMsg.errorText;
    }
  }

  unloadLot() {
    this.communicationService.send({type: 'cmd', command: 'unload'});
  }

  private updateStatus(status: Status) {
    this.status = status;
    this.updateInputConfigs();
    this.updateButtonConfigs();
  }

  private updateInputConfigs() {
    this.lotNumberInputConfig.disabled = this.status.state !== SystemState.initialized;
    this.lotNumberInputConfig = Object.assign({}, this.lotNumberInputConfig);
  }

  private updateButtonConfigs() {
    this.loadLotButtonConfig.disabled = this.status.state !== SystemState.initialized;
    this.loadLotButtonConfig = Object.assign({}, this.loadLotButtonConfig);

    this.unloadLotButtonConfig.disabled = this.status.state !== SystemState.ready;
    this.unloadLotButtonConfig = Object.assign({}, this.unloadLotButtonConfig);
  }

  private validateLotNumber(errorMsg: {errorText: string}): boolean {
    let pattern = /^[1-9][0-9]{5}[.][0-9]{3}$/ ;

    if (pattern.test(this.lotNumberInputConfig.value)) {
      errorMsg.errorText = '';
      return true;
    } else {
      errorMsg.errorText = 'A lot number should be in 6.3 format like \"123456.123\"';
      return false;
    }
  }
}
