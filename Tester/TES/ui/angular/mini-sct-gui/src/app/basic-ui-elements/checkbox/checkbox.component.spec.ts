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

  it('should support disabled property', () => {
    component.checkboxConfig.disabled = true;
    fixture.detectChanges();
    expect(debugElement.query(By.css('.disabled'))).toBeDefined();
    component.checkboxConfig.disabled = false;
    fixture.detectChanges();
    expect(debugElement.query(By.css('.disabled'))).toBeNull();
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
