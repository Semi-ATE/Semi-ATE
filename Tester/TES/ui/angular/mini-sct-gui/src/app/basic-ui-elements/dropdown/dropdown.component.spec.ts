import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DropdownComponent } from './dropdown.component';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from 'src/app/test-stuff/auxillary-test-functions';

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

  it('should support selected index', () => {
    let expectedSelectedIndex = 2;
    component.dropdownConfig.labelText = 'Test';
    component.dropdownConfig.items = [
      {description:'desc 1', value: 1},
      {description:'desc 2', value: 2},
      {description:'desc 3', value: 3},
    ];
    component.dropdownConfig.selectedIndex = expectedSelectedIndex;
    fixture.detectChanges();
    let selectedInnerText = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(selectedInnerText).toBe(component.dropdownConfig.items[expectedSelectedIndex].description);
  });

  it('should support disabled status', async () => {
    component.dropdownConfig.selectedIndex = 0;
    component.dropdownConfig.items = [
      {description:'desc 1', value: 1},
      {description:'desc 2', value: 2},
      {description:'desc 3', value: 3},
    ];

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.dropbox .selected'))?.nativeElement.innerText ===
      component.dropdownConfig.items[component.dropdownConfig.selectedIndex].description,
      'Selected option should be ' + component.dropdownConfig.items[component.dropdownConfig.selectedIndex].description
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('.dropbox')).classes.disabled,
      'Element should not be disabled'
    );

    component.dropdownConfig.disabled = true;

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.dropbox')).classes.disabled,
      'Element should be disabled'
    );
  });

  it('should be possible to select a new option', async () => {
    let expectedSelectedIndex = 2;
    component.dropdownConfig.labelText = 'Test';
    component.dropdownConfig.items = [
      {description:'desc 1', value: 1},
      {description:'desc 2', value: 2},
      {description:'desc 3', value: 3},
    ];
    component.dropdownConfig.selectedIndex = expectedSelectedIndex;
    fixture.detectChanges();

    let selectedInnerText = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(selectedInnerText).toBe(component.dropdownConfig.items[expectedSelectedIndex].description);

    debugElement.query(By.css('li.selected')).nativeElement.click();
    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('.closed')),
      'Dropbox did not open.'
    );

    debugElement.queryAll(By.css('li')).find(e => e.nativeElement.innerText === component.dropdownConfig.items[0].description).nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.closed')),
      'Dropbox did not close.'
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('li.selected')).nativeElement.innerText === component.dropdownConfig.items[0].description,
      'Selected list element does not show the expected value "' + component.dropdownConfig.items[0].description + '"'
    );
  });

  it('should not call dropdownChangeEvent function when dropdown is disabled', () => {
    spyOn(component.dropdownChangeEvent, 'emit');
    component.dropdownConfig.disabled = true;
    component.selectedItem(1);
    expect(component.dropdownChangeEvent.emit).not.toHaveBeenCalled();
  });

  describe('initDropdown', () => {
    it('should get initialized value when it called ', () => {
      let expectedValue = 2;
      let dropdownItems = [{description:'desc 1', value: 1}, {description:'desc 2', value: 2}];
      component.dropdownConfig.initDropdown('', false, dropdownItems, 1);

      expect(component.dropdownConfig.value).toEqual(expectedValue);
    });

    it('should support value when items and selectedIndex are optional', () => {
      component.dropdownConfig.initDropdown('', false, [], -1);
      expect(component.dropdownConfig.value).toEqual(undefined);

      let items = [{description:'desc 1', value: 1}, {description:'desc 2', value: 2}];
      component.dropdownConfig.initDropdown('', false, items, 0);

      expect(component.dropdownConfig.value).toEqual(1);
    });
  });
});
