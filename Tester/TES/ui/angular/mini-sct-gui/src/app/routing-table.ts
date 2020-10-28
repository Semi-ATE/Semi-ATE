import { SystemControlComponent } from './system-control/system-control.component';
import { SystemInformationComponent } from './system-information/system-information.component';
import { Routes } from '@angular/router';
import { SystemConsoleComponent } from './system-console/system-console.component';
import { StdfRecordViewComponent } from './stdf-record-view/stdf-record-view.component';

export enum MenuItem {
  Info = 'information',
  Control = 'control',
  Records = 'records',
  Logging = 'logging',
}

export const MINISCT_ROUTES: Routes = [
  {path: '', redirectTo: MenuItem.Info, pathMatch: 'full'},
  {path: MenuItem.Info, component: SystemInformationComponent},
  {path: MenuItem.Control, component: SystemControlComponent},
  {path: MenuItem.Records, component: StdfRecordViewComponent},
  {path: MenuItem.Logging, component: SystemConsoleComponent},
  {path: '**', redirectTo: MenuItem.Info},
];
