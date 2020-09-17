import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import * as constants from 'src/app/services/mockserver-constants';
import { DebugComponent } from './debug.component';

describe('DebugComponent', () => {
  let component: DebugComponent;
  let fixture: ComponentFixture<DebugComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DebugComponent ]
    })
    .compileComponents();
  }));

  afterAll( () => {
    document.getElementById(constants.MOCK_SEVER_SERVICE_NEVER_REMOVABLE_ID)?.remove();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DebugComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create debug component', () => {
    expect(component).toBeTruthy();
  });
});
