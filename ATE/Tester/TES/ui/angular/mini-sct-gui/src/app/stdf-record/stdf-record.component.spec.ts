import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordComponent } from './stdf-record.component';
import { StdfRecordType, StdfRecordProperty, STDF_RECORD_ATTRIBUTES, Stdf } from 'src/app/stdf/stdf-stuff';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('StdfRecordComponent', () => {
  let component: StdfRecordComponent;
  let fixture: ComponentFixture<StdfRecordComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StdfRecordComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StdfRecordComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create stdf-record component', () => {
    expect(component).toBeTruthy();
  });

  it('should show all entries', () => {
    let expectedEntries: StdfRecordProperty[] = [
      {key: 'label1', value: 1},
      {key: 'label2', value: 'Value'},
      {key: 'label3', value: true},
      {key: 'label4', value: 'langer Wert. Passt der noch drauf?'},
      {key: 'label5', value: 0.0027636238462363473},
    ];

    component.stdfRecord = {
      type: StdfRecordType.Pir,
      values: expectedEntries
    };
    fixture.detectChanges();

    let expectedStrings = expectedEntries.map(e => e.key + ':\n' + e.value);
    let entries = debugElement.queryAll(By.css('.recordEntries li'));
    let currentStrings = entries?.map(e => e.nativeElement.innerText);
    expect(currentStrings).toEqual(jasmine.arrayWithExactContents(expectedStrings));
  });

  describe('computeMultichoiceConfigurationForTestFlagValue', () => {
    it('should compute label starting with "Test Flag"', () => {
      let configuration = component.computeMultichoiceConfigurationForTestFlagValue(1);
      expect(configuration.label).toMatch('^Test Flag*', 'Label has to start with "Test Flag"');
    });

    it('should always compute 8 items', () => {
      let numbers = [
        -50,
        1,
        10,
        17,
        100,
        500,
        8000
      ];
      for (let i = 0; i < numbers.length; ++i) {
        let configuration = component.computeMultichoiceConfigurationForTestFlagValue(numbers[i]);
        expect(configuration.items.length).toBe(8, 'We expect always 8 items');
      }
    });

    it('should compute "unknown" when more than 8 items ', () => {
      expect((component as any).getTestflagBitDescription(9)).toEqual('unknown');
    });
  });

  describe('siteNumberToLetter', () => {
    it('should compute "A" when site number is 0', () => {
      let siteNumber = 0;
     expect((component as any).siteNumberToLetter(siteNumber)).toEqual('A');
    });

    it('should compute "B" when site number is 1', () => {
      let siteNumber = 1;
     expect((component as any).siteNumberToLetter(siteNumber)).toEqual('B');
    });

    it('should compute "undefined" when site number is smaller as 0', () => {
      let siteNumber = -1;
     expect((component as any).siteNumberToLetter(siteNumber)).toEqual(undefined);
    });
  });

  describe('getScaledResult, getScaledHighLimit, getScaledLowLimit', () => {
    it('should compute scaled values from stdf record', () => {
      let expectedEntries: StdfRecordProperty[] = [
        {key:STDF_RECORD_ATTRIBUTES.RESULT, value: 1.23},
        {key:STDF_RECORD_ATTRIBUTES.RES_SCAL, value: 6},
        {key:STDF_RECORD_ATTRIBUTES.UNITS, value: 'AMPS'},
        {key:STDF_RECORD_ATTRIBUTES.HI_LIMIT, value: -123},
        {key:STDF_RECORD_ATTRIBUTES.HLM_SCAL, value: -3},
        {key:STDF_RECORD_ATTRIBUTES.LO_LIMIT, value: 0.44},
        {key:STDF_RECORD_ATTRIBUTES.LLM_SCAL, value: 0},
        {key:STDF_RECORD_ATTRIBUTES.C_RESFMT, value: '%7.3f'},
        {key:STDF_RECORD_ATTRIBUTES.C_LLMFMT, value: '%7.3f'},
        {key:STDF_RECORD_ATTRIBUTES.C_HLMFMT, value: '%7.3f'},
      ];

      component.stdfRecord = {
        type: StdfRecordType.Ptr,
        values: expectedEntries
      };

      Stdf.computeScaledResultFromSTDF(component.stdfRecord);
      expect(component.getScaledResult()).toEqual('1230000.000 uAMPS');
      Stdf.computeScaledHighLimitFromSTDF(component.stdfRecord);
      expect(component.getScaledHighLimit()).toEqual(' -0.123 KAMPS');
      Stdf.computeScaledLowLimitFromSTDF(component.stdfRecord);
      expect(component.getScaledLowLimit()).toEqual('  0.440 AMPS');
    });

    it('should compute value as a string when RESULT, HI_LIMIT, LO_LIMIT are not numbers', () => {
      let expectedEntries: StdfRecordProperty[] = [
        {key:STDF_RECORD_ATTRIBUTES.RESULT, value: 'inifinity'},
        {key:STDF_RECORD_ATTRIBUTES.RES_SCAL, value: 6},
        {key:STDF_RECORD_ATTRIBUTES.UNITS, value: 'AMPS'},
        {key:STDF_RECORD_ATTRIBUTES.HI_LIMIT, value: 'inf'},
        {key:STDF_RECORD_ATTRIBUTES.HLM_SCAL, value: 0.44},
        {key:STDF_RECORD_ATTRIBUTES.LO_LIMIT, value: '-inf'},
        {key:STDF_RECORD_ATTRIBUTES.LLM_SCAL, value: 0},
        {key:STDF_RECORD_ATTRIBUTES.C_RESFMT, value: '%7.2f'},
        {key:STDF_RECORD_ATTRIBUTES.C_LLMFMT, value: '%7.2f'},
        {key:STDF_RECORD_ATTRIBUTES.C_HLMFMT, value: '%7.2f'},
      ];

      component.stdfRecord = {
        type: StdfRecordType.Ptr,
        values: expectedEntries
      };

      Stdf.computeScaledResultFromSTDF(component.stdfRecord);
      expect(component.getScaledResult()).toEqual('inifinity');
      Stdf.computeScaledHighLimitFromSTDF(component.stdfRecord);
      expect(component.getScaledHighLimit()).toEqual('inf');
      Stdf.computeScaledLowLimitFromSTDF(component.stdfRecord);
      expect(component.getScaledLowLimit()).toEqual('-inf');
    });
  });

  describe('getTestNumber, getHeadNumber, getTestText, getTestFlag', () => {
    it('should compute values from stdf record', () => {
      let expectedEntries: StdfRecordProperty[] = [
        {key:STDF_RECORD_ATTRIBUTES.TEST_NUM, value: 123},
        {key:STDF_RECORD_ATTRIBUTES.HEAD_NUM, value: 0},
        {key:STDF_RECORD_ATTRIBUTES.TEST_TXT, value: 'IsupVm1V'},
        {key:STDF_RECORD_ATTRIBUTES.TEST_FLG, value: 0},
      ];

      component.stdfRecord = {
        type: StdfRecordType.Ptr,
        values: expectedEntries
      };

      expect(component.getTestNumber()).toEqual(123);
      expect(component.getHeadNumber()).toEqual(0);
      expect(component.getTestText()).toEqual('IsupVm1V');
      expect(component.getTestFlag()).toEqual(0);
    });
  });

  describe('getPassStatus', () => {
    it('should compute the pass/fail status and the matching text color', () => {
      let expectedEntries: StdfRecordProperty[] = [
        {key:STDF_RECORD_ATTRIBUTES.TEST_FLG, value: 0},
      ];

      component.stdfRecord = {
        type: StdfRecordType.Ptr,
        values: expectedEntries
      };

      expect(component.getPassStatus()).toEqual('P');
      expect(component.passOrFailTextColor).toEqual('#0AC473');
      expect(component.getTestFlag()).toEqual(0);

      expectedEntries[0].value = -1;
      component.getPassStatus();

      expect(component.passOrFail).toEqual('F');
      expect(component.passOrFailTextColor).toEqual('#BD2217');
      expect(component.getTestFlag()).toEqual(-1);
    });
  });

  describe('getSiteNumber', () => {
    it('should compute the pass/fail status and the matching text color', () => {
      let expectedEntries: StdfRecordProperty[] = [
        {key:STDF_RECORD_ATTRIBUTES.SITE_NUM, value: 0},
      ];

      component.stdfRecord = {
        type: StdfRecordType.Ptr,
        values: expectedEntries
      };

      expect(component.getSiteNumber()).toEqual('A');

      expectedEntries[0].value = 1;
      expect(component.getSiteNumber()).toEqual('B');
    });
  });
});
