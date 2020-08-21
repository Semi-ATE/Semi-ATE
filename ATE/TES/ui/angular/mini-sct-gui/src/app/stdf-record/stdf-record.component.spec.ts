import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordComponent } from './stdf-record.component';
import { StdfRecord, StdfRecordType, StdfRecordLabelType, StdfRecordValueType } from 'src/app/stdf/stdf-stuff';
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
    let expectedEntries: [StdfRecordLabelType, StdfRecordValueType][] = [
      ['label1', 1],
      ['label2', 'Value'],
      ['label3', true],
      ['label4', 'langer Wert. Passt der noch drauf?'],
      ['label5', 0.0027636238462363473],
    ];

    component.stdfRecord = {
      type: StdfRecordType.Pir,
      values: expectedEntries
    };
    fixture.detectChanges();

    let expectedStrings = expectedEntries.map(e => e[0] + ':\n' + e[1]);
    let entries = debugElement.queryAll(By.css('.recordEntries li'));
    let currentStrings = entries?.map(e => e.nativeElement.innerText);
    expect(currentStrings).toEqual(jasmine.arrayWithExactContents(expectedStrings));
  });
});
