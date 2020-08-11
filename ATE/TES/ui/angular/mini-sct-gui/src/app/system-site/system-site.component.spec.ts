import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { SystemSiteComponent } from './system-site.component';
import { DebugElement } from '@angular/core';
import * as constants from './../services/mockserver-constants';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { MockServerService } from '../services/mockserver.service';
import { FormsModule } from '@angular/forms';
import { CommunicationService } from '../services/communication.service';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from './../test-stuff/auxillary-test-functions';

describe('SystemSiteComponent', () => {
  let component: SystemSiteComponent;
  let fixture: ComponentFixture<SystemSiteComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SystemSiteComponent, CardComponent],
      schemas: [],
      providers: [
        CommunicationService
      ],
      imports: [FormsModule]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    mockServerService = new MockServerService();
    fixture = TestBed.createComponent(SystemSiteComponent);
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

  it('should have elements', () => {
    const doc = fixture.debugElement.nativeElement;
    expect(doc.querySelector('.table')).toBeDefined();

    expect(fixture.nativeElement.querySelectorAll('th')[0]
                                .textContent.trim())
                                .toBe('Type');
    expect(fixture.nativeElement.querySelectorAll('th')[1]
                                .textContent.trim())
                                .toBe('Site ID');
    expect(fixture.nativeElement.querySelectorAll('th')[2]
                                .textContent.trim())
                                .toBe('State');
  });

  it('should show "TestApp" entry if server sends message ' + JSON.stringify(constants.TEST_APP_MESSAGE_SITE_7_TESTING), async () => {

    function entryFound(containingString: string): boolean {
      return debugElement.queryAll(By.css('tr')).filter(r => r.nativeElement.innerText.includes(containingString)).length > 0;
    }

    // configure the mock server to send the following message
    let spy = spyOn<any>(component, 'handleServerMessage').and.callThrough();

    expect(entryFound('TestApp')).toBeFalsy('At the beginning there is no row containing "TestApp"');

    // mock some server message
    mockServerService.setMessages([
      constants.TEST_APP_MESSAGE_SITE_7_TESTING,
    ]);

    await expectWaitUntil(
      () => {
        component.ngOnInit();
        fixture.detectChanges();
      },
      () => entryFound('TestApp'),
      'No entry including text "TestApp" could be found');

    // message handler funtion should have been called
    expect(spy).toHaveBeenCalled();

    // the entry must be unique
    let entry = debugElement.queryAll(By.css('tr')).filter(r => r.nativeElement.innerText.includes('TestApp'));
    expect(entry.length).toBe(1);

    // check the cintent of the entry
    let tds = entry[0].queryAll(By.css('td'));
    let currentEntryText = [];
    tds.forEach(d => currentEntryText.push(d.nativeElement.innerText));
    expect(currentEntryText).toEqual(jasmine.arrayWithExactContents(['TestApp', '7', 'testing']));

  });

});
