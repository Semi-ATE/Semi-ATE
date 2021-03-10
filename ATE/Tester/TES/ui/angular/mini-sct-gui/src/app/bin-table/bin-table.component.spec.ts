import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StoreModule } from '@ngrx/store';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { TableComponent } from '../basic-ui-elements/table/table.component';
import { binReducer } from '../reducers/bintable.reducer';
import { statusReducer } from '../reducers/status.reducer';
import { AppstateService } from '../services/appstate.service';
import { MockServerService } from '../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { BinTableComponent } from './bin-table.component';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';
import { By } from '@angular/platform-browser';

describe('BinTableComponent', () => {
  let component: BinTableComponent;
  let fixture: ComponentFixture<BinTableComponent>;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let expectedTableHeaders = [
    'Name',
    'Soft Bin',
    'Hard Bin',
    'Type',
    'Total'
  ];

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [BinTableComponent, CardComponent, TableComponent],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer,
          binTable: binReducer
        })
      ]
    }).compileComponents();
  }));

  beforeEach(() => {
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);

    fixture = TestBed.createComponent(BinTableComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    mockServerService.ngOnDestroy();
  });

  it('should create bin-table commponent', () => {
    expect(component).toBeTruthy();
  });

  it('should show label text', () => {
    expect(component.captionCardConfiguration.labelText).toBe('Bin Table');
  });

  it('should display bin table headerRow', () => {
    expectedTableHeaders.forEach(e => {
      expect(component.binTableConfiguration.headerRow.filter(h => h.text.includes(e)).length).toBeGreaterThan(0);
    });
  });

  it('should display bin data', async () => {
    expect(component.binTable.length).toEqual(0);

    let tableHeadersElement = debugElement.queryAll(By.css('.tableHeader li'));
    expect(tableHeadersElement.length).toBe(5);

    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
      constants.BIN_ENTRIES
    ]);

    await expectWaitUntil(
       () => fixture.detectChanges(),
       () => debugElement.queryAll(By.css('.tableRow li')).length > 0,
       'No bin table entry has been found',
     );
    let tableRowsElement = debugElement.queryAll(By.css('.tableRow li')).map(e => e.nativeElement.innerText);
    expect(tableRowsElement[0]).toEqual('Alarm');
  });
});
