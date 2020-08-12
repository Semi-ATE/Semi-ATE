import { MenuItem } from 'src/app/app-routing.module';
import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { CommunicationService } from 'src/app/services/communication.service';
import { SystemState } from 'src/app/models/status.model';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.scss']
})
export class MenuComponent implements OnInit {
  systemState: SystemState;
  menuItem: any;

  constructor(private readonly communicationService: CommunicationService, private readonly router: Router) {
    this.systemState = SystemState.connecting;
    this.menuItem = MenuItem;
    communicationService.message.subscribe(msg => this.handleServerMessage(msg));
  }

  private handleServerMessage(serverMessage: any) {
    if (serverMessage && serverMessage.payload && serverMessage.payload.state) {
      if (this.systemStateChanged(serverMessage.payload.state)) {
        this.systemState = serverMessage.payload.state;
      }
    }
  }

  private systemStateChanged(state: SystemState): boolean {
    return state !== this.systemState;
  }

  ngOnInit() {
  }

  isDisabled(menuItem: MenuItem): boolean {
    switch (menuItem) {
      case MenuItem.Info:
      case MenuItem.Logging:
        return false;
      case MenuItem.Results:
        return this.resultsDisabled();
      case MenuItem.Control:
        return this.controlDisabled();
    }
  }

  private resultsDisabled(): boolean {
    switch (this.systemState) {
      case SystemState.connecting:
      case SystemState.initialized:
      case SystemState.unloading:
      case SystemState.loading:
        return true;
    }
    return false;
  }

  private controlDisabled(): boolean {
    switch (this.systemState) {
      case SystemState.connecting:
        return true;
    }
    return false;
  }

  isActive(path: string): boolean {
    return this.router.url === '/' + path;
  }
}
