import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HeaderComponent } from './header.component';
import { MenuComponent } from '../../menu/menu.component';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { RouterModule } from '@angular/router';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';
import { resultReducer } from 'src/app/reducers/result.reducer';
import { consoleReducer } from 'src/app/reducers/console.reducer';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';
import { SystemStatusComponent } from 'src/app/system-status/system-status.component';
import { DebugElement } from '@angular/core';
import { ButtonComponent } from 'src/app/basic-ui-elements/button/button.component';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HeaderComponent, MenuComponent, SystemStatusComponent, ButtonComponent ],
      imports: [
        FormsModule,
        RouterTestingModule,
        RouterModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer // key must be equal to the key define in interface AppState, i.e. userSettings
        }),]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create header component', () => {
    expect(component).toBeTruthy();
  });

  it(`should have as title 'MiniSCT'`, () => {
    const app = fixture.debugElement.componentInstance;
    expect(app.title).toEqual('MiniSCT');
  });
  it('should render title in a h1 tag', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('MiniSCT');
  });

  it('should contain an app-system-status tag', () => {
    let componentElement = debugElement.nativeElement.querySelectorAll('app-system-status');
    expect(componentElement).not.toEqual(null);
    expect(componentElement.length).toBe(1);
  });

  it('should contain an app-menu tag', () => {
    let componentElement = debugElement.nativeElement.querySelectorAll('app-menu');
    expect(componentElement).not.toEqual(null);
    expect(componentElement.length).toBe(1);
  });
});
