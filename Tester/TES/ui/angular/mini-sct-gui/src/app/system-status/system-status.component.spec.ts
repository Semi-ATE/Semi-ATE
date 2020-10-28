import { ComponentFixture, TestBed, async } from '@angular/core/testing';
import { SystemStatusComponent } from './system-status.component';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { MockServerService } from '../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';
import { AppstateService } from '../services/appstate.service';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../reducers/status.reducer';

describe('SystemStatusComponent', () => {
  let component: SystemStatusComponent;
  let fixture: ComponentFixture<SystemStatusComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SystemStatusComponent ],
      providers: [ ],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
        })
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);

    fixture = TestBed.createComponent(SystemStatusComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create status component', () => {
    expect(component).toBeTruthy();
  });

  it('should show a correct circle color', async () => {

    // condition when we found our green circle
    function foundCircle(color: string): boolean {
      let element = debugElement.query(By.css('span.' + color));
      if (element) {
        return true;
      }
      return false;
    }

    let spy = spyOn<any>(component, 'adaptState').and.callThrough();

    // send initialized message
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_INITIALIZED]);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => foundCircle('green'),
      'No green circle could be found'
    );

    expect(spy).toHaveBeenCalled();

    // send error message
    mockServerService.setMessages([constants.MESSAGE_WHEN_SYSTEM_STATUS_ERROR]);

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => foundCircle('red'),
      'No red circle could be found'
    );
    expect(spy).toHaveBeenCalled();
  });

});
