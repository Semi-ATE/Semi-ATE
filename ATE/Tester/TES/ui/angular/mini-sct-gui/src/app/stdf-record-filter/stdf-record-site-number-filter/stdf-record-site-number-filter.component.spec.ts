import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordSiteNumberFilterComponent } from './stdf-record-site-number-filter.component';
import { StdfRecordType } from '../../stdf/stdf-stuff';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from '../../test-stuff/auxillary-test-functions';
import * as constants from './../../services/mockserver-constants';
import { CheckboxComponent } from '../../basic-ui-elements/checkbox/checkbox.component';
import { FormsModule } from '@angular/forms';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from '../../reducers/status.reducer';
import { resultReducer } from '../../reducers/result.reducer';
import { consoleReducer } from '../../reducers/console.reducer';
import { userSettingsReducer } from '../../reducers/usersettings.reducer';
import { AppstateService } from '../../services/appstate.service';
import { StdfRecordFilterService } from '../../services/stdf-record-filter-service/stdf-record-filter.service';
import { DebugElement } from '@angular/core';
import { InputComponent } from '../../basic-ui-elements/input/input.component';
import { StorageMap } from '@ngx-pwa/local-storage';
import { MockServerService } from '../../services/mockserver.service';
import { SiteNumberFilterSetting } from '../../models/storage.model';

describe('StdfRecordSiteNumberFilterComponent', () => {
  let component: StdfRecordSiteNumberFilterComponent;
  let fixture: ComponentFixture<StdfRecordSiteNumberFilterComponent>;
  let appStateService: AppstateService;
  let filterService: StdfRecordFilterService;
  let debugElement: DebugElement;
  let storage: StorageMap;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        StdfRecordSiteNumberFilterComponent,
        CheckboxComponent,
        InputComponent
      ],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
          results: resultReducer, // key must be equal to the key define in interface AppState, i.e. results
          consoleEntries: consoleReducer, // key must be equal to the key define in interface AppState, i.e. consoleEntries
          userSettings: userSettingsReducer, // key must be equal to the key define in interface AppState, i.e. userSettings
        }),
      ],
    })
    .compileComponents();
  }));

  beforeEach( async () => {
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    mockServerService = TestBed.inject(MockServerService);
    appStateService = TestBed.inject(AppstateService);
    filterService = TestBed.inject(StdfRecordFilterService);
    fixture = TestBed.createComponent(StdfRecordSiteNumberFilterComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach( () => {
    mockServerService.ngOnDestroy();
  });


  async function waitProperInitialization() {
    let expectedLabelText = 'Show only the following sites';
    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.queryAll(By.css('label')).some(e => e.nativeElement.innerText === expectedLabelText),
      'Expected label text ' + expectedLabelText + ' was not found.'
    );
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Site Filter', () => {
    describe('siteNumberFromString', () => {
      it('should return -1 in case that the input is larger than the maxSite number', () => {
        let testCase = {
          input: '12',
          minSite: 0,
          maxSite: 6,
          expectedResult: -1,
        };
        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case that the input is smaller than the minSite number', () => {
        let testCase = {
          input: '1',
          minSite: 2,
          maxSite: 6,
          expectedResult: -1,
        };
        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case that the input is not a integer number provided as string', () => {
        let testCase = {
          input: '1.0',
          minSite: 0,
          maxSite: 6,
          expectedResult: -1,
        };

        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case that the input is "hallo"', () => {
        let testCase = {
          input: 'hallo',
          minSite: 0,
          maxSite: 6,
          expectedResult: -1,
        };

        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return -1 in case that the input is a negative integer number', () => {
        let testCase = {
          input: '-1',
          minSite: -1,
          maxSite: 6,
          expectedResult: -1,
        };

        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return valid site number', () => {
        let testCase = {
          input: '1',
          minSite: 1,
          maxSite: 1,
          expectedResult: 1,
        };

        expect(
          (component as any).siteNumberFromString(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });
    });

    describe('siteNumbersFromRange', () => {
      it('should return empty array, i.e. [] in case that the input is invalid', () => {
        let testCases = [
          {
            input: '1',  // invalid as '1' is not a range like '1-4'
            minSite: 1,
            maxSite: 6,
            expectedResult: [],
          },
          {
            input: '2-6', // invalid as 2 is less than minSite
            minSite: 3,
            maxSite: 6,
            expectedResult: [],
          },
          {
            input: '3-1', // invalid as range should be ordered like '1-3'
            minSite: 1,
            maxSite: 15,
            expectedResult: [],
          },
          {
            input: '2-7', // invalid because 7 is greater than maxSite
            minSite: 2,
            maxSite: 6,
            expectedResult: [],
          }
        ];

        testCases.forEach(t =>
          expect(
            (component as any).siteNumbersFromRange(
              t.input,
              t.minSite,
              t.maxSite
            )
          ).toEqual(t.expectedResult));
      });

      it('should return valid site numbers', () => {
        let testCase = {
          input: '2-7',
          minSite: 2,
          maxSite: 7,
          expectedResult: [2, 3, 4, 5, 6, 7],
        };

        expect(
          (component as any).siteNumbersFromRange(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });
    });

    describe('computeSitesOfInterest', () => {
      it('should return [] if input is ""', () => {
        let result = [];
        const EMPTY_STRING = '';
        (component as any).computeSitesOfInterest(EMPTY_STRING, 0, 3);
        expect((component as any).selectedSiteNumbers.length).toEqual(0);
        expect((component as any).selectedSiteNumbers).toEqual(result);
      });

      it('should return "undefined" in case of any error', () => {
        let testCase = {
          input: '1,b-3', // invalid because 'b-3' is not a valid range
          minSite: 0,
          maxSite: 14,
          expectedResult: undefined,
        };

        expect(
          (component as any).computeSitesOfInterest(
            testCase.input,
            testCase.minSite,
            testCase.maxSite
          )
        ).toEqual(testCase.expectedResult);
      });

      it('should return site numbers in case that the input is valid', () => {
        let testCases = [
          {
            input: '0,1',
            minSite: 0,
            maxSite: 2,
            expectedResult: [0, 1],
          },
          {
            input: '3-4',
            minSite: 2,
            maxSite: 5,
            expectedResult: [3, 4],
          },
          {
            input: '1,2,3,4-5,1-5',
            minSite: 0,
            maxSite: 5,
            expectedResult: [1, 2, 3, 4, 5],
          }
        ];

        testCases.forEach(t =>
          expect(
            (component as any).computeSitesOfInterest(
              t.input,
              t.minSite,
              t.maxSite
            )
          ).toEqual(t.expectedResult));
      });
    });

    describe('Checkbox', () => {
      it('should be rendered in DOM', async () => {
        let containedString = 'Show only the following sites';
        let found = () => {
          if(debugElement.query(By.css('#siteNumberCheckbox'))?.nativeElement.innerText.includes(containedString))
            return true;
          return false;
        };
        await expectWaitUntil(
          () => fixture.detectChanges(),
          found,
          'Checkbox with label text containing "' + containedString + '" could not be found'
        );
      });

      it('should call function updateFilterAndPublish when clicked', async () => {
        (component as any).maxSiteNumber = 0;
        spyOn<any>(component, 'getMaxSiteNumber');
        await  waitProperInitialization();
        let spy = spyOn<any>(component, 'updateFilterAndPublish');
        debugElement
          .query(By.css('#siteNumberCheckbox .toggle'))
          .nativeElement.click();
        fixture.detectChanges();
        expect(spy).toHaveBeenCalled();
      });
    });

    describe('siteNumberFilterCheckboxChanged', () => {
      it('should call updateFilterAndPublish', () => {
        let updateFilterSpy = spyOn((component as any), 'updateFilterAndPublish');
        (component as any).maxSiteNumber = 3;
        component.siteNumberInputConfig.value = '2';
        component.filterChanged();
        expect(updateFilterSpy).toHaveBeenCalled();
      });
    });

    describe('Input field for site numbers', () => {
      it('should be rendered in DOM', () => {
        expect(
          debugElement.query(By.css('.siteNumberFilter'))
        ).toBeTruthy();
      });

      it('should call function updateFilterAndPublish on change event and valid input', async () => {
        let spy = spyOn<any>(component, 'updateFilterAndPublish');
        (component as any).maxSiteNumber = 2;
        component.siteNumberInputConfig.value = '1';
        debugElement.query(By.css('#siteNumberInput input')).nativeElement.dispatchEvent(new Event('change'));
        expect(spy).toHaveBeenCalled();
      });
    });

    it('should only show stdf records of site 0 if site filter is active and configured to see only site 0', async () => {
      // we need some records with different site numbers
      let records = [[
        {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 0}]},
        {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 1}]},
        {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 2}]},
        {type: StdfRecordType.Ptr, values: [{key: 'SITE_NUM', value: 3}]}
      ]];
      // get records into our component
      appStateService.stdfRecords = records;
      filterService.filteredRecords = records;

      // set max site number
      (component as any).maxSiteNumber = 3;
      expect(filterService.filteredRecords.length).toEqual(records.length);
      component.siteNumberCheckboxConfig.checked = true;
      component.siteNumberInputConfig.value = '0';

      component.filterChanged();

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => filterService.filteredRecords.reduce( (a,c) => a + c.length, 0) === 1,
        'There should be a single PTR record for site number 0'
      );

      let allrecords = filterService.filteredRecords.reduce( (a,c) => a.concat(...c), []);
      expect(allrecords.length).toEqual(1);
      expect(allrecords[0].type).toEqual(StdfRecordType.Ptr);
    });

    describe('siteNumberFilterValueChanged', () => {
      it('should set an error text in case of ivalid input like ",,1"', () => {
        const INVALID_INPUT = ',,1';
        component.siteNumberCheckboxConfig.checked = true;
        component.siteNumberInputConfig.value = INVALID_INPUT;
        component.filterChanged();
        expect(component.siteNumberInputConfig.errorMsg).toContain('error');
      });
    });
  });

  it('should return value of maxSiteNumber as -1 if Status is undefined', () => {
    const maxSiteNumber = -1;
    (component as any).getMaxSiteNumber(undefined);
    expect((component as any).maxSiteNumber).toEqual(maxSiteNumber);
  });

  describe('isSubsetOfSelectedSiteNumbers', () => {
    it('should return "true" if the provided site number array is a subset of the site number array of this component', () => {
      const providedArray = [4,1];
      (component as any).selectedSiteNumbers = [1,2,3,4];
      expect((component as any).isSubsetOfSelectedSiteNumbers(providedArray)).toEqual(true);
    });
    it('should return "false" if the provided site number array is NOT a subset of the site number array of this component', () => {
      const providedArray = [4,1,5];
      (component as any).selectedSiteNumbers = [1,2,3,4];
      expect((component as any).isSubsetOfSelectedSiteNumbers(providedArray)).toEqual(false);
    });
  });

  describe('restoreSettings', () => {
    it('should deactivate site number filter', async (done) => {
      // we mock some system state and wait until the component applied thsi state
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_READY,
      ]);

      // wait until component is initialized
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () =>(component as any).maxSiteNumber === constants.MESSAGE_WHEN_SYSTEM_STATUS_READY.payload.sites.length -1,
        'Did not initialized properly' );
      // setup
      component.siteNumberCheckboxConfig.checked = true;
      storage.clear().subscribe( async () => {
        // test
        (component as any).restoreSettings();

        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => !component.siteNumberCheckboxConfig.checked,
          'Restore settings did not deactivate site filter' );
        done();
      });
    });
    it('should apply settings from storage', async (done) => {
      // we mock some system state and wait until the component applied thsi state
      mockServerService.setRepeatMessages(false);
      mockServerService.setMessages([
        constants.MESSAGE_WHEN_SYSTEM_STATUS_READY
      ]);

      // wait until component is initialized
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () =>(component as any).maxSiteNumber === constants.MESSAGE_WHEN_SYSTEM_STATUS_READY.payload.sites.length -1,
        'Did not initialized properly' );
      // setup
      let setting: SiteNumberFilterSetting = {
        enabled: true,
        selectedSites: '1,3'
      };
      storage.set((component as any).getStorageKey(), setting).subscribe( async () => {
        // test
        (component as any).restoreSettings();
        await expectWaitUntil(
          () => fixture.detectChanges(),
          () => {
            let result = component.siteNumberCheckboxConfig.checked === setting.enabled;
            result = result && component.siteNumberInputConfig.value === setting.selectedSites;
            return result;
          },
          'Restore settings did not apply settings from storage' );
        // expect((component as any).selectedSiteNumbers).toEqual([1,3]);
        done();
      });
    });
  });
});
