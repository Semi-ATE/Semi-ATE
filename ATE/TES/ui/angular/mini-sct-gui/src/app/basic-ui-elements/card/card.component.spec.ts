import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { CardComponent, CardStyle } from './card.component';
import { DebugElement, NO_ERRORS_SCHEMA } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('CardComponent', () => {
  let component: CardComponent;
  let fixture: ComponentFixture<CardComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CardComponent ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CardComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
  });

  it('should create card component', () => {
    expect(component).toBeTruthy();
  });

  it('should support shadow, i.e. boxShadow', () => {
    component.cardConfiguration.shadow = true;
    fixture.detectChanges();

    let card = debugElement.query(By.css('.cardShadow'));
    let cardElement = card.nativeElement;

    expect(getComputedStyle(cardElement).boxShadow).toBe('rgba(0, 0, 0, 0.4) 0px 4px 8px 0px');

    component.cardConfiguration.shadow = false;
    fixture.detectChanges();

    card = debugElement.query(By.css('.cardShadow'));
    expect(card).toBeFalsy();

    card = debugElement.query(By.css('.card'));
    cardElement = card.nativeElement;

    expect(getComputedStyle(cardElement).boxShadow).toBe('none');
  });

  it('should support labelText', () => {
    component.cardConfiguration.labelText = 'Label';
    fixture.detectChanges();

    let card = debugElement.query(By.css('h2'));
    let cardElement = card.nativeElement;

    expect(cardElement.innerHTML).toBe('Label');
  });

  it('should support cardStyle to be rowStyle', () => {
    component.cardConfiguration.cardStyle = CardStyle.ROW_STYLE;
    fixture.detectChanges();

    let card = debugElement.query(By.css('.card'));
    let cardElement = card.nativeElement;

    expect(cardElement.getAttribute('class')).toContain(CardStyle.ROW_STYLE);

    expect(getComputedStyle(cardElement).display).toBe('flex');
    expect(getComputedStyle(cardElement).flexDirection).toBe('row');
  });

  it('should support cardStyle to be columnStyle', () => {
    component.cardConfiguration.cardStyle = CardStyle.COLUMN_STYLE;
    fixture.detectChanges();

    let card = debugElement.query(By.css('.card'));
    let cardElement = card.nativeElement;

    expect(cardElement.getAttribute('class')).toContain(CardStyle.COLUMN_STYLE);

    expect(getComputedStyle(cardElement).display).toBe('flex');
    expect(getComputedStyle(cardElement).flexDirection).toBe('column');
  });

});
