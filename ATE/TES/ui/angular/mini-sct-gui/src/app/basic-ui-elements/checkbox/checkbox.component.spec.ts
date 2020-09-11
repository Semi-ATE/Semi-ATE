import { FormsModule } from '@angular/forms';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { CheckboxComponent } from './checkbox.component';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('CheckboxComponent', () => {
  let component: CheckboxComponent;
  let fixture: ComponentFixture<CheckboxComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [CheckboxComponent],
      schemas: [],
      imports: [FormsModule]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CheckboxComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create checkbox component', () => {
    expect(component).toBeTruthy();
  });

  it('should be checked', async(() => {
    component.checkboxConfig.checked = true;
    component.checkboxConfig.labelText = 'I am a checked checkbox';
    fixture.detectChanges();

    // wait for checkbox beeing checked
    fixture.whenStable().then(() => {
      expect(debugElement.query(By.css('input')).nativeElement.checked).toBe(true);

      component.checkboxConfig.checked = false;
      component.checkboxConfig.labelText = 'I am a unchecked checkbox';
      fixture.detectChanges();

      // wait for checkbox being unchecked
      fixture.whenStable().then(() => {
        expect(debugElement.query(By.css('input')).nativeElement.checked).toBe(false);
      });
    });
  }));

  it('Input field should be disabled', () => {
    component.checkboxConfig.disabled = true;
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('disabled')).toBeTruthy('Checkbox is expected to be disabled');

    component.checkboxConfig.disabled = false;
    fixture.detectChanges();

    expect(inputElement.hasAttribute('disabled')).toBeFalsy('Checkbox is expected to be enabled, i.e. to have no attribute disabled');
  });

  it('should support labelText', () => {
    component.checkboxConfig.labelText = 'Test Labeltext';
    fixture.detectChanges();

    let checkbox = debugElement.query(By.css('.checkbox'));
    let checkboxElement = checkbox.nativeElement;

    expect(checkboxElement.textContent).toContain('Test Labeltext');
  });

  it('should call checkboxValueChange function when clicked', () => {
    spyOn(component, 'checkboxValueChange').and.callThrough();

    let checkbox = debugElement.query(By.css('input'));
    let checkboxElement = checkbox.nativeElement;

    let checkedStatusBeforeClick = checkboxElement.checked;

    checkboxElement.click();
    fixture.detectChanges();

    expect(component.checkboxValueChange).toHaveBeenCalledWith(!checkedStatusBeforeClick);
  });
});
