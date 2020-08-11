import { Injectable } from '@angular/core';
import { WebSocketSubject } from 'rxjs/webSocket';
import { map } from 'rxjs/operators';
import { WebsocketService } from './websocket.service';
import { BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION } from './../services/mockserver-constants';
@Injectable({
  providedIn: 'root'
})
export class CommunicationService {

  message: WebSocketSubject<any>;

  constructor(private readonly wsService: WebsocketService) {
    this.message = (wsService.connect(BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION).pipe(map(
      (response: any) => {
      return response;
    }
    )) as WebSocketSubject<any>);
   }

  send(json: any) {
    this.wsService.send(json);
  }

  mqttSubscribe(topic: string, qos: number = 0) {
    this.wsService.send({type: 'mqtt.subscribe', payload: {topic, qos}});
  }

  mqttPublish(topic: string, payload: object, qos: number = 0, retain: boolean = true) {
    this.wsService.send({type: 'mqtt.publish', payload: { topic, payload, retain }});
  }
}
