import { SystemControlComponent } from './system-control/system-control.component';
import { SystemInformationComponent } from './system-information/system-information.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes, Router } from '@angular/router';
import { SystemSiteComponent } from './system-site/system-site.component';
import { SystemConsoleComponent } from './system-console/system-console.component';

export enum MenuItem {
  Info = 'information',
  Control = 'control',
  Results = 'results',
  Logging = 'logging',
}

export const routes: Routes = [
  {path: '', redirectTo: MenuItem.Info, pathMatch: 'full'},
  {path: MenuItem.Info, component: SystemInformationComponent},
  {path: 'control', component: SystemControlComponent},
  {path: 'results', component: SystemSiteComponent},
  {path: 'logging', component: SystemConsoleComponent},
  {path: '**', redirectTo: MenuItem.Info},
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forRoot(routes, { enableTracing: true, initialNavigation: false, useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule {
  constructor(private readonly router: Router) {
    this.router.navigate(['/information'], { replaceUrl: true });
  }
}
