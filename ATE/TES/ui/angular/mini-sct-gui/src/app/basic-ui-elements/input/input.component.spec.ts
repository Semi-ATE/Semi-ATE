import { FormsModule } from '@angular/forms';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { InputComponent } from './input.component';
import { InputType } from './input-config';

describe('InputComponent', () => {
  let component: InputComponent;
  let fixture: ComponentFixture<InputComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InputComponent ],
      schemas: [],
      imports: [FormsModule]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(InputComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create input component', () => {
    expect(component).toBeTruthy();
  });

  it('Input field should be disabled', () => {
    component.inputConfig.disabled = true;
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('disabled')).toBeTruthy('input field is expected to be disabled');

    component.inputConfig.disabled = false;
    fixture.detectChanges();

    expect(!inputElement.hasAttribute('disabled')).toBeTruthy('input field is expected to be enabled, i.e. to have no attribute disabled');
  });

  it('should support textColor', () => {
     component.inputConfig.textColor = '#030402';
     fixture.detectChanges();

     let input = debugElement.query(By.css('input'));
     let inputElement = input.nativeElement;

     expect(inputElement.getAttribute('style')).toContain('color: rgb(3, 4, 2)');
  });

  it('should support type being text', () => {
    component.inputConfig.type = InputType.text;
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('type')).toBeTruthy('input field has type of "text"');
    expect(inputElement.getAttribute('type')).toBe('text');
  });

  it('should support type being number', () => {
    component.inputConfig.type = InputType.number;
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('type')).toBeTruthy('input field has type of "number"');
    expect(inputElement.getAttribute('type')).toBe('number');
  });

  it('should support placeholder attribute', () => {
    component.inputConfig.placeholder = 'Test text - placeholder';
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('placeholder')).toBeTruthy('input field has attribute "placeholder"');
    expect(inputElement.getAttribute('placeholder')).toBe('Test text - placeholder', 'The placeholder attrribute should be set to "Test text - placeholder"');
  });

  it('should show error message', () => {
   let erroMessage = 'input field has error';
   component.inputConfig.errorMsg = erroMessage;
   fixture.detectChanges();

   let span = debugElement.query(By.css('span'));
   let spanElement = span.nativeElement;

   expect(spanElement).toBeTruthy();
   expect(spanElement.textContent).toBe(erroMessage);
  });

  it('should not show error message', () => {
    let erroMessage = '';
    component.inputConfig.errorMsg = erroMessage;
    fixture.detectChanges();

    let span = debugElement.query(By.css('span'));

    expect(span).toBe(null);
  });

  it('should clear error message on user input', () => {
    // 1st set an error message
    let erroMessage = 'Error message should be removed on user input';
    component.inputConfig.errorMsg = erroMessage;
    fixture.detectChanges();

    let span = debugElement.query(By.css('span'));
    let spanElement = span.nativeElement;

    expect(spanElement).toBeTruthy();
    expect(spanElement.textContent).toBe(erroMessage);

    // 2nd perform user input
    spyOn(component, 'resetErrorMsg').and.callThrough();
    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    inputElement.value = 'user';
    inputElement.dispatchEvent(new Event('focus'));

    expect(component.resetErrorMsg).toHaveBeenCalled();

    // 3rd check that the error message has gone
    fixture.detectChanges();
    // update span element
    span = debugElement.query(By.css('span'));
    expect(span).toBe(null);
  });
});
