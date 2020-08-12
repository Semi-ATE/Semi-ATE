import { CommunicationService } from './../services/communication.service';
import { Component, OnInit } from '@angular/core';
import { CardConfiguration, CardStyle } from './../basic-ui-elements/card/card.component';

export class SystemSiteEntry {
  type: string;
  siteId: string;
  state: string;

  constructor(type: string, siteId: string, state: string) {
    this.type = type;
    this.siteId = siteId;
    this.state = state;
  }

  equals(other: SystemSiteEntry): boolean {
    return other.siteId === this.siteId && other.type === this.type;
  }
}

@Component({
  selector: 'app-system-site',
  templateUrl: './system-site.component.html',
  styleUrls: ['./system-site.component.scss']
})

export class SystemSiteComponent implements OnInit {
  systemSiteCardConfiguration: CardConfiguration;

  readonly entries: SystemSiteEntry[];

  constructor(private readonly communicationService: CommunicationService) {
    this.systemSiteCardConfiguration = new CardConfiguration();
    this.entries = [];

    communicationService.message.subscribe(msg => this.handleServerMessage(msg));
  }
  private handleServerMessage(serverMessage: any) {
    if (serverMessage.payload && serverMessage.payload.payload && serverMessage.payload.topic && (serverMessage.type === 'mqtt.onmessage')) {
      let id = this.extractId(serverMessage.payload.topic);
      let payload = serverMessage.payload.payload;
      if (id && (payload.type === 'status')) {
        if (serverMessage.payload.topic.includes('TestApp')) {
          this.updateTestApp(id, payload.state);
        } else if (serverMessage.payload.topic.includes('Control')) {
          this.updateControl(id, payload.state);
        }
      }
    }
  }

  ngOnInit() {
    this.systemSiteCardConfiguration.cardStyle = CardStyle.ROW_STYLE_FOR_SYSTEM;
    this.systemSiteCardConfiguration.labelText = 'System Sites';
  }

  private extractId(mqttTopic: string): string {
    const topicSplit: string[] = mqttTopic.split('/');
    let result: string = topicSplit[topicSplit.length - 1].replace(/site/g, '');
    return result;
  }

  private  updateControl(id: string, state: string): void {
    this.updateEntry('Control', id, state);
  }

  private  updateTestApp(id: string, state: string): void {
    this.updateEntry('TestApp', id, state);
  }

  private updateEntry(entryName: string, id: string , state: string): void {
    let entry = new SystemSiteEntry(entryName, id, state);
    let found = false;

    for (let i = 0; i < this.entries.length; ++i) {
      if (this.entries[i].equals(entry)) {
        this.entries[i].state = entry.state;
        found = true;
        break;
      }
    }
    if (!found) {
      this.entries.push(entry);
    }
  }
}
