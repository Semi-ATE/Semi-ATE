import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { StdfRecordComponent } from './stdf-record.component';
import { StdfRecord, StdfRecordType, StdfRecordPropertyKey, StdfRecordPropertyValue, StdfRecordProperty } from 'src/app/stdf/stdf-stuff';
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
});
