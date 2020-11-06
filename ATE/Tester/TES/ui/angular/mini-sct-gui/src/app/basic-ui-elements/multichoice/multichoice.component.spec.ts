import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { initMultichoiceEntry } from './multichoice-config';

import { MultichoiceComponent } from './multichoice.component';

describe('MultichoiceComponent', () => {
  let component: MultichoiceComponent;
  let debugElement: DebugElement;
  let fixture: ComponentFixture<MultichoiceComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MultichoiceComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MultichoiceComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should reflact multichoice configuration in DOM', () => {
    let multichoiceConfig = {
      readonly: false,
      items: [
        initMultichoiceEntry('test 1', false, 'orange', 'green'),
        initMultichoiceEntry('test 2', true, '#339956', 'black')
      ],
      label: 'Label'
    };

    component.multichoiceConfig = multichoiceConfig;
    fixture.detectChanges();

    // check label text
    let label = debugElement.query(By.css('label'));
    expect(label.nativeElement.innerText).toEqual(multichoiceConfig.label);

    // check readonly property
    let item = debugElement.query(By.css('.items'));
    expect(item.classes.readonly !== undefined).toEqual(multichoiceConfig.readonly);

    let items = debugElement.queryAll(By.css('li'));

    // label check
    expect(items.map(e => e.nativeElement.innerText))
      .toEqual(
        jasmine.arrayWithExactContents(
          multichoiceConfig.items.map(e => e.label)
        )
      );

    // checked check
    expect(items.map(e => e.classes.checked !== undefined))
      .toEqual(
        jasmine.arrayWithExactContents(
          multichoiceConfig.items.map(e => e.checked)
        )
      );
  });

  describe('changeItem', () => {
    it('should not emit change event if configured as "readonly"', () => {
      component.multichoiceConfig.readonly = true;
      let spy = spyOn(component.multichoiceChangeEvent, 'emit');
      fixture.detectChanges();
      component.changeItem(0);
      expect(spy).not.toHaveBeenCalled();
    });

    it('should emit change event if not configured as "readonly"', () => {
      component.multichoiceConfig.readonly = false;
      component.multichoiceConfig.items = [
        initMultichoiceEntry('label 1', false)
      ];
      let spy = spyOn(component.multichoiceChangeEvent, 'emit');
      fixture.detectChanges();
      component.changeItem(0);
      expect(spy).toHaveBeenCalled();
    });

  });
});
