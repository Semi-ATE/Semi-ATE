import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { MultichoiceConfiguration } from './multichoice-config';

@Component({
  selector: 'app-multichoice',
  templateUrl: './multichoice.component.html',
  styleUrls: ['./multichoice.component.scss']
})
export class MultichoiceComponent implements OnInit {

  @Input()
  multichoiceConfig: MultichoiceConfiguration;

  @Output()
  multichoiceChangeEvent: EventEmitter<void>;

  constructor() {
    this.multichoiceConfig = {
      readonly: false,
      label: '',
      items: []
    };
    this.multichoiceChangeEvent = new EventEmitter<void>();
  }

  ngOnInit(): void {
  }

  changeItem(itemIndex: number) {
    if (this.multichoiceConfig.readonly)
      return;
    this.multichoiceConfig.items[itemIndex].checked = !this.multichoiceConfig.items[itemIndex].checked;
    this.multichoiceChangeEvent.emit();
  }
}
