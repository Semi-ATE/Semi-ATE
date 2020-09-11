import { SystemControlComponent } from './system-control/system-control.component';
import { SystemInformationComponent } from './system-information/system-information.component';
import { Routes } from '@angular/router';
import { ResultComponent } from './result/result.component';
import { SystemConsoleComponent } from './system-console/system-console.component';

export enum MenuItem {
  Info = 'information',
  Control = 'control',
  Results = 'results',
  Logging = 'logging',
}

export const MINISCT_ROUTES: Routes = [
  {path: '', redirectTo: MenuItem.Info, pathMatch: 'full'},
  {path: MenuItem.Info, component: SystemInformationComponent},
  {path: MenuItem.Control, component: SystemControlComponent},
  {path: MenuItem.Results, component: ResultComponent},
  {path: MenuItem.Logging, component: SystemConsoleComponent},
  {path: '**', redirectTo: MenuItem.Info},
];
