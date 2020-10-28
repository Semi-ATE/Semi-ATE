import { Injectable, OnDestroy } from '@angular/core';
import { WebSocketSubject } from 'rxjs/webSocket';
import { map, takeUntil } from 'rxjs/operators';
import { WebsocketService } from './websocket.service';
import { AppState } from '../app.state';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION } from '../constants';
@Injectable({
  providedIn: 'root'
})
export class CommunicationService  implements OnDestroy {

  message: WebSocketSubject<any>;
  private connectionId: string;
  private readonly ngUnsubscribe: Subject<void>;

  constructor(private readonly wsService: WebsocketService, private readonly store: Store<AppState>) {
    this.ngUnsubscribe = new Subject<void>();
    this.message = (
      wsService.connect(BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION).pipe(
        map(
          (response: any) => {
            return response;
          }
        )
      ) as WebSocketSubject<any>
    );

    this.store.select('connectionId')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe( e => this.connectionId = e);
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  send(json: any) {
    json.connectionid = this.connectionId;
    this.wsService.send(json);
  }
}
