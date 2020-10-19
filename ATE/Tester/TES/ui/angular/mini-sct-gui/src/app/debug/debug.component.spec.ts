import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import * as constants from 'src/app/services/mockserver-constants';
import { DebugComponent } from './debug.component';
import { MockServerService } from '../services/mockserver.service';

describe('DebugComponent', () => {
  let mockServerService: MockServerService;
  let component: DebugComponent;
  let fixture: ComponentFixture<DebugComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DebugComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    fixture = TestBed.createComponent(DebugComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });

  it('should create debug component', () => {
    expect(component).toBeTruthy();
  });
});
