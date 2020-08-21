import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { ResultComponent } from './result.component';
import { DebugElement } from '@angular/core';
import * as constants from '../services/mockserver-constants';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { MockServerService } from '../services/mockserver.service';
import { FormsModule } from '@angular/forms';
import { SystemBinStatusComponent } from '../system-bin-status/system-bin-status.component';
import { AppstateService } from '../services/appstate.service';
import { Store, StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { consoleReducer } from '../reducers/console.reducer';
import { SiteBinInformationComponent } from '../site-bin-information/site-bin-information.component';
import { StdfRecordViewComponent } from '../stdf-record-view/stdf-record-view.component';
import { StdfRecordComponent } from '../stdf-record/stdf-record.component';
import { CheckboxComponent } from '../basic-ui-elements/checkbox/checkbox.component';
import { ButtonComponent } from '../basic-ui-elements/button/button.component';
import { userSettingsReducer } from 'src/app/reducers/usersettings.reducer';

describe('ResultComponent', () => {
  let component: ResultComponent;
  let fixture: ComponentFixture<ResultComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
         StdfRecordViewComponent,
         StdfRecordComponent,
         ResultComponent,
         CardComponent,
         SystemBinStatusComponent,
         SiteBinInformationComponent,
         CheckboxComponent,
         ButtonComponent
      ],
      schemas: [],
      providers: [
      ],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer // key must be equal to the key define in interface AppState, i.e. userSettings
        })
      ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);
    fixture = TestBed.createComponent(ResultComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID).remove();
  });

  it('should create site component', () => {
    expect(component).toBeTruthy();
  });

  it('should table show up', () => {
    const doc = fixture.debugElement.nativeElement;
    expect(doc.querySelector('.table')).toBeDefined();
  });
});
