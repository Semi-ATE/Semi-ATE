import { Component, OnInit } from '@angular/core';
import { select, Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import { AppState } from 'src/app/app.state';
import { Status } from 'src/app/models/status.model';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {
  status$: Observable<Status>;

  constructor(private readonly _Store: Store<AppState>) {
    this.status$ = this._Store.pipe(select('systemStatus'));
  }

  ngOnInit() {
  }

}
