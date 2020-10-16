import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from 'src/app/test-stuff/auxillary-test-functions';
import { TabComponent } from './tab.component';

describe('TabComponent', () => {
  let component: TabComponent;
  let fixture: ComponentFixture<TabComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TabComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TabComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show labels', () => {
    let expectedLabels = ['General', 'Site A', 'Site B'];
    component.tabConfig.labels = expectedLabels;
    fixture.detectChanges();

    let liElement = debugElement.queryAll(By.css('li')).map(e => e.nativeElement.innerText);
    expect(liElement).toEqual(expectedLabels);
  });

  it('should support selected index', () => {
    let expectedSelectedIndex = 1;
    component.tabConfig.labels = ['General', 'Site A', 'Site B'];
    component.tabConfig.selectedIndex = expectedSelectedIndex;
    fixture.detectChanges();
    let selectedInnerText = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(selectedInnerText).toBe(component.tabConfig.labels[expectedSelectedIndex]);
  });

  it('should support disabled status', async () => {
    component.tabConfig.selectedIndex = 0;
    component.tabConfig.labels = ['General', 'Site A', 'Site B'];

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.tabElement .selected'))?.nativeElement.innerText ===
      component.tabConfig.labels[component.tabConfig.selectedIndex],
      'Selected option should be ' + component.tabConfig.labels[component.tabConfig.selectedIndex]
    );

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => !debugElement.query(By.css('.tabElement li')).classes.disabled,
      'Elements should not be disabled'
    );

    component.tabConfig.disabled = [true, true, true];

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('.tabElement li')).classes.disabled,
      'Elements should be disabled'
    );
  });

  it('should be possible to select a new tab', async () => {
    component.tabConfig.labels = ['General', 'Site A', 'Site B'];
    fixture.detectChanges();

    let selectedInnerText = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(component.tabConfig.selectedIndex).toEqual(0);
    expect(selectedInnerText).toBe(component.tabConfig.labels[0]);

    let expectedSelectedIndex = 1;
    debugElement.queryAll(By.css('li'))[expectedSelectedIndex].nativeElement.click();

    await expectWaitUntil(
      () => fixture.detectChanges(),
      () => debugElement.query(By.css('li.selected')).nativeElement.innerText === component.tabConfig.labels[expectedSelectedIndex],
      'Selected tab element does not show the expected value "' + component.tabConfig.labels[expectedSelectedIndex] + '"'
    );
  });

  it('should emit an event when function selectTab called', () => {
    let spy = spyOn(component.tabChangeEvent, 'emit');
    component.selectTab(2);
    fixture.detectChanges();

    expect(spy).toHaveBeenCalled();
  });

  it('should not emit an event when tab is disabled', () => {
    let spy = spyOn(component.tabChangeEvent, 'emit');

    component.tabConfig.labels = ['General', 'Site A', 'Site B'];
    component.tabConfig.disabled = [false, true, false];

    component.selectTab(1);
    fixture.detectChanges();

    expect(spy).not.toHaveBeenCalled();

    component.selectTab(2);
    fixture.detectChanges();

    expect(spy).toHaveBeenCalled();
  });

  it('should support initialized values when initTab function called', () => {
    component.tabConfig.initTab([false, false, false], ['General', 'Tab 1', 'Tab 2'], 2);
    fixture.detectChanges();

    let tabElement = debugElement.queryAll(By.css('li')).map(e => e.nativeElement.innerText);
    expect(tabElement).toEqual(['General', 'Tab 1', 'Tab 2']);

    let selectTabElement = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(selectTabElement).toEqual('Tab 2');
  });

  it('should display selected label when the selectedIndex is the same as the expected index', () => {
    let expectedSelectIndex = 1;
    component.tabConfig.selectedIndex = expectedSelectIndex;
    component.tabConfig.labels = ['General', 'Tab 1', 'Tab 2'];
    fixture.detectChanges();

    component.selectTab(expectedSelectIndex);

    let selectTabElement = debugElement.query(By.css('li.selected')).nativeElement.innerText;
    expect(selectTabElement).toEqual('Tab 1');
  });
});
