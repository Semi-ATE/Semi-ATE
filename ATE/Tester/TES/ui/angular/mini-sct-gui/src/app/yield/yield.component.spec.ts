import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { StoreModule } from '@ngrx/store';
import { CardComponent } from '../basic-ui-elements/card/card.component';
import { TabComponent } from '../basic-ui-elements/tab/tab.component';
import { TableComponent } from '../basic-ui-elements/table/table.component';
import { SystemState } from '../models/status.model';
import { consoleReducer } from '../reducers/console.reducer';
import { resultReducer } from '../reducers/result.reducer';
import { statusReducer } from '../reducers/status.reducer';
import { userSettingsReducer } from '../reducers/usersettings.reducer';
import { yieldReducer } from '../reducers/yield.reducer';
import { AppstateService, MessageTypes } from '../services/appstate.service';
import { MockServerService } from '../services/mockserver.service';
import * as constants from '../services/mockserver-constants';
import { YieldComponent } from './yield.component';
import { expectWaitUntil } from '../test-stuff/auxillary-test-functions';
import { YieldSetting } from '../models/storage.model';
import { StorageMap } from '@ngx-pwa/local-storage';
import { getSiteName } from '../stdf/stdf-stuff';

describe('YieldComponent', () => {
  let component: YieldComponent;
  let fixture: ComponentFixture < YieldComponent > ;
  let debugElement: DebugElement;
  let mockServerService: MockServerService;
  let storage: StorageMap;

  beforeEach(async (() => {
    TestBed.configureTestingModule({
      declarations: [YieldComponent, TabComponent, CardComponent, TableComponent],
      imports: [
        StoreModule.forRoot({
          systemStatus: statusReducer,
          results: resultReducer,
          consoleEntries: consoleReducer,
          userSettings: userSettingsReducer,
          yield: yieldReducer
        })
      ]
    })
    .compileComponents();
  }));

  beforeEach(async () => {
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    mockServerService = TestBed.inject(MockServerService);
    TestBed.inject(AppstateService);

    fixture = TestBed.createComponent(YieldComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    mockServerService.ngOnDestroy();
  });

  it('should create yield component', () => {
    expect(component).toBeTruthy();
  });

  it('should show label text', () => {
    expect(component.yieldCardConfiguration.labelText).toBe('Yield');
  });

  let noYieldEntryMsg = 'No yield entries';
  it('should show "'+ noYieldEntryMsg + '", when system state is ' + JSON.stringify(SystemState.connecting), () => {
    expect((component as any).status.state).toBe('connecting');

    let messageElement = debugElement.query(By.css('p'));

    expect(messageElement.nativeElement.innerText).toEqual(noYieldEntryMsg);
  });

  describe('When yield data is available', () => {
    it('should display yield data', async () => {
      mockServerService.setMessages([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
        constants.YIELD_ENTRIES
      ]);

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => debugElement.queryAll(By.css('li')).length > 0,
        'Can not find elements for yield data');

      let expectedTabLabels = ['Total', 'A', 'B', 'C', 'D'];
      let tabLabels = debugElement.queryAll(By.css('.tabLabel li')).map(e => e.nativeElement.innerText);

      expect(tabLabels).toEqual(expectedTabLabels);
    });

    it('should display table headerRow', () => {
      let expectedTableHeaders = ['', 'Amount', 'Percentage'];

      expectedTableHeaders.forEach( e => {
        expect(component.yieldTableConfiguration.headerRow.filter(h => h.text.includes(e)).length).toBeGreaterThan(0);
      });
    });

    it('should change current yield data automatically in case that a new yield data arrives', () => {
      expect((component as any).yieldData.length).toEqual(0);

      let expectedYieldTableEntries = [ 'test 1', '200', '50' ];

      (component as any).yieldData = [
        {
          name: 'test 1',
          siteid: '-1',
          count: 200,
          value: 50
        }
      ];
      (component as any).updateYieldTable();
      fixture.detectChanges();

      let yieldTableEntries = debugElement.queryAll(By.css('.tableRow li')).map(e => e.nativeElement.innerText);

      expect(yieldTableEntries).toEqual(expectedYieldTableEntries);
    });

    describe('updateYieldTab', () => {
      it('should update the selected tab', async () => {
        mockServerService.setMessages([
          constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
          constants.YIELD_ENTRIES
        ]);

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => debugElement.queryAll(By.css('li')).length > 0,
          'Can not find elements for yield data');

        expect(component.yieldTabConfiguration.selectedIndex).toEqual(0);
        expect(debugElement.query(By.css('.selected')).nativeElement.innerText).toBe('Total');

        component.yieldTabConfiguration.selectedIndex = 2;
        (component as any).updateYieldTab();
        fixture.detectChanges();

        expect(debugElement.query(By.css('.selected')).nativeElement.innerText).toBe('B');
      });
    });
  });

  async function waitProperInitialization() {
    mockServerService.setMessages([
      constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
      constants.YIELD_ENTRIES
    ]);

    let expectedTabLabelText = 'Total';

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.queryAll(By.css('.selected')).some(e => e.nativeElement.innerText === expectedTabLabelText),
      'Expected tab label text ' + expectedTabLabelText + ' was not found.'
    );
  }

  describe('restoreSelectedTabIndex', () => {
    it('should restore selected tab index from localStorage', async (done) => {
      await waitProperInitialization();

      component.yieldTabConfiguration.selectedIndex = 100000;
      (component as any).restoreSelectedTabIndex();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => component.yieldTabConfiguration.selectedIndex === 0,
        'Restore selected tab index from localStorage failed');
      done();
    });
  });

  it('should apply settings from storage', async (done) => {
    await waitProperInitialization();

    let setting: YieldSetting = {
      selectedTabIndex: 100
    };

    storage.set((component as any).getStorageKey(), setting).subscribe(async () => {
      (component as any).restoreSelectedTabIndex();
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => component.yieldTabConfiguration.selectedIndex === 100,
        'Restore settings did not apply settings from storage');
      done();
    });
  });

  describe('tabChanged', () => {
    it('should call updateYieldTable and saveSettings', () => {
      let spyOnUpdateYieldTable = spyOn<any>(component, 'updateYieldTable');
      let spyOnSaveSettings = spyOn<any>(component, 'saveSettings');

      component.tabChanged();

      expect(spyOnSaveSettings).toHaveBeenCalled();
      expect(spyOnUpdateYieldTable).toHaveBeenCalled();
    });
  });

  describe('getSiteName', () => {
    it('should map numbers between 0 and 15 to letter, i.e. 0 maps to letter "A"', () => {
      expect(getSiteName(0)).toBe('A');
      expect(getSiteName(1)).toBe('B');
      expect(getSiteName(2)).toBe('C');
      expect(getSiteName(3)).toBe('D');
      expect(getSiteName(4)).toBe('E');
      expect(getSiteName(5)).toBe('F');
      expect(getSiteName(6)).toBe('G');
      expect(getSiteName(7)).toBe('H');
      expect(getSiteName(8)).toBe('I');
      expect(getSiteName(9)).toBe('J');
      expect(getSiteName(10)).toBe('K');
      expect(getSiteName(11)).toBe('L');
      expect(getSiteName(12)).toBe('M');
      expect(getSiteName(13)).toBe('N');
      expect(getSiteName(14)).toBe('O');
      expect(getSiteName(15)).toBe('P');
    });

    it('should map numbers greater than 15 to "unknown"', () => {
      expect(getSiteName(16)).toBe('unknown');
      expect(getSiteName(100)).toBe('unknown');
      expect(getSiteName(1234)).toBe('unknown');
    });
  });
});
