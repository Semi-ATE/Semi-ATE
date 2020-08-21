import { Injectable } from '@angular/core';
import { WebSocket, Server } from 'mock-socket';
import { interval, Observable } from 'rxjs';
import * as constants from '../services/mockserver-constants';
import { formatDate } from '@angular/common';

let globalMockServer;

@Injectable({
  providedIn: 'root'
})

export class MockServerService {

  private mockServer: Server;
  private timer: Observable<number>;
  private msgs: any[];
  private currentIndex: number;
  private repeatMessages: boolean;
  private updateTime: boolean;

  constructor() {
    this.msgs = new Array<any>();
    this.repeatMessages = false;
    this.updateTime = true;
    this.makeReadyForTest();
    this.setSendMessageInterval(1000);
  }

  setSendMessageInterval(milliseconds: number) {
    this.timer = interval(milliseconds);
    if (this.mockServer) {
      this.mockServer.on('connection', socket => {
        socket.on('message', data => {
          this.handleClientMessage(data, socket);
        });
        this.timer.subscribe( () => {
          this.sendMsg(socket);
        });
      });
    }
  }

  appendMessage(message: any) {
    this.msgs.push(message);
  }

  clearMessages() {
    this.setMessages([]);
  }

  setMessages(messages: any[]) {
    this.currentIndex = 0;
    this.msgs = messages;
  }

  setRepeatMessages(repeat: boolean) {
    this.repeatMessages = repeat;
  }

  setUpdateTime(updateTime: boolean) {
    this.updateTime = updateTime;
  }

  private makeReadyForTest() {
    if (!document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)) {
      let div = document.createElement('div');
      div.setAttribute('id', constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID);
      div.innerHTML = 'MOCK SERVER SERVICE IS RUNNING';
      document.body.appendChild(div);
    }
    if (!globalMockServer) {
      globalMockServer = new Server(constants.BACKEND_URL_RUNNING_IN_PYTHON_MASTER_APPLICATION);
      this.mockServer = globalMockServer;
    } else {
      this.mockServer = globalMockServer;
    }
  }

  private sendMsg(socket: WebSocket): any {
    if (this.currentIndex >= this.msgs.length) {
      if (this.repeatMessages) {
        this.currentIndex = 0;
      } else {
        this.currentIndex = this.msgs.length - 1;
      }
    }

    if (this.indexValid()) {
      this.addTimeToMsg();
      socket.send(JSON.stringify(this.msgs[this.currentIndex]));
    }

    this.currentIndex++;
  }

  private indexValid(): boolean {
    return (this.msgs.length !== 0 && this.currentIndex < this.msgs.length);
  }

  private handleClientMessage(data: any, socket: WebSocket): any {
  }

  private addTimeToMsg() {
    if (this.indexValid() &&  this.updateTime) {
      let msg = this.msgs[this.currentIndex];
      if (!msg.payload) {
        msg.payload = {};
      }
      msg.payload.systemTime = formatDate(Date.now(), 'medium', 'en-US');
    }
  }


}
