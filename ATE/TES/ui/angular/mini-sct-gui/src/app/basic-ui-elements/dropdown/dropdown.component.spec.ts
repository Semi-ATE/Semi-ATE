import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DropdownComponent } from './dropdown.component';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('DropdownComponent', () => {
  let component: DropdownComponent;
  let fixture: ComponentFixture<DropdownComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DropdownComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DropdownComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show label text', () => {
    let expectedLabel = 'Dropdown Label';
    component.dropdownConfig.labelText = expectedLabel;
    fixture.detectChanges();
    expect(debugElement.query(By.css('label')).nativeElement.innerText).toEqual(expectedLabel);
  });

  it('should support attribute disabled', () => {
    expect(debugElement.query(By.css('select')).nativeElement.hasAttribute('disabled')).toBeFalse();
    component.dropdownConfig.disabled = true;
    fixture.detectChanges();
    expect(debugElement.query(By.css('select')).nativeElement.hasAttribute('disabled')).toBeTrue();
  });

  it('should support selected index', () => {
    let expectedSellectedIndex = 2;
    component.dropdownConfig.labelText = 'Test';
    component.dropdownConfig.items = [
      {description:'desc 1', value: 1},
      {description:'desc 2', value: 2},
      {description:'desc 3', value: 3},
    ];
    component.dropdownConfig.selectedIndex = expectedSellectedIndex;
    fixture.detectChanges();
    let selectedIndex = debugElement.query(By.css('select')).nativeElement.selectedIndex;
    expect(selectedIndex).toBe(expectedSellectedIndex);
  });
});
