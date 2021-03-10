import { FormsModule } from '@angular/forms';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { InputComponent } from './input.component';
import { InputType } from './input-config';
import { StorageMap } from '@ngx-pwa/local-storage';
import { MockServerService } from 'src/app/services/mockserver.service';
import { StoreModule } from '@ngrx/store';
import { statusReducer } from 'src/app/reducers/status.reducer';

describe('InputComponent', () => {
  let component: InputComponent;
  let fixture: ComponentFixture<InputComponent>;
  let debugElement: DebugElement;
  let storage: StorageMap;
  let mockServerService: MockServerService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InputComponent ],
      schemas: [],
      imports: [
        FormsModule,
        StoreModule.forRoot({
          systemStatus: statusReducer, // key must be equal to the key define in interface AppState, i.e. systemStatus
        }),
      ]
    }).compileComponents();
  }));

  beforeEach(async () => {
    storage = TestBed.inject(StorageMap);
    await storage.clear().toPromise();
    mockServerService = TestBed.inject(MockServerService);
    fixture = TestBed.createComponent(InputComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    mockServerService.ngOnDestroy();
  });

  it('should create input component', () => {
    expect(component).toBeTruthy();
  });

  it('should support disabled attribute', () => {
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

  it('should support autocompleteId attribute', () => {
    let autocompleteId = 'TestLotNumber';
    component.inputConfig.autocompleteId = autocompleteId;
    fixture.detectChanges();

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.hasAttribute('autocompleteId')).toBeTruthy('input field has attribute "autocompleteId"');
    expect(inputElement.getAttribute('autocompleteId')).toBe(autocompleteId, `The autocompleteId attrribute should be set to ${autocompleteId}`);
  });

  describe('ErrorMessage', () => {
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
      spyOn(component as any, 'resetErrorMsg').and.callThrough();
      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      inputElement.value = 'user';
      inputElement.dispatchEvent(new Event('focus'));

      expect((component as any).resetErrorMsg).toHaveBeenCalled();

      // 3rd check that the error message and value of input has gone
      fixture.detectChanges();
      // update span element
      span = debugElement.query(By.css('span'));
      expect(span).toBe(null);
      expect(inputElement.textContent).toBe('');
    });

    it('should clear error message when onBlur() called', () => {
      let erroMessage = 'Error message should be removed on blur';
      component.inputConfig.errorMsg = erroMessage;
      fixture.detectChanges();

      let span = debugElement.query(By.css('span'));
      let spanElement = span.nativeElement;

      expect(spanElement).toBeTruthy();
      expect(spanElement.textContent).toBe(erroMessage);

      component.onBlur();
      fixture.detectChanges();

      span = debugElement.query(By.css('span'));
      expect(span).toBe(null);
    });
  });

  it('should emit event when press Enter', () => {
    let spy = spyOn(component.carriageReturnEvent, 'emit');

    const input = debugElement.query(By.css('input'));
    const inputElement = input.nativeElement;

    inputElement.value = 'user input';
    inputElement.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter'}));

    expect(spy).toHaveBeenCalled();
    expect(inputElement.value).toEqual('user input');
  });

  it('should emit change event when changes are made', () => {
    let expectValueOfInput = 'Input changed';
    let spy = spyOn(component.inputChangeEvent, 'emit');

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    expect(inputElement.value).toEqual('');

    inputElement.value = expectValueOfInput;
    inputElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(spy).toHaveBeenCalled();
    expect(inputElement.value).toEqual(expectValueOfInput);
  });

  it('should call selectedEntry when onEnter is called and historyItemIndex is "0"', () => {
    let spy = spyOn(component as any, 'selectedEntry');
    component.historyItemIndex = 0;
    (component as any).onEnter();
    fixture.detectChanges();

    expect(spy).toHaveBeenCalled();
  });

  describe('preventDefault', () => {
    it('should call "preventDefault" in case arrow-up-key is pressed', () => {
      let keyEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' });
      let spy = spyOn(keyEvent, 'preventDefault');
      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;
      inputElement.dispatchEvent(keyEvent);
      fixture.detectChanges();

      expect(spy).toHaveBeenCalled();
    });

    it('should call "preventDefault" when the key is invalid e.g. "Down"', () => {
      let keyEvent = new KeyboardEvent('keydown', { key: 'Down' });
      let spy = spyOn(keyEvent, 'preventDefault');

      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      component.inputConfig.validCharacterRegexp = /([0-9]|\.)/;
      inputElement.dispatchEvent(keyEvent);
      fixture.detectChanges();

      expect(spy).toHaveBeenCalled();
    });
  });

  it('should show the selected value by mouse click', () => {
    let selectedEntryIndex = 1;
    let expectFilteredHistories = ['111111.111', '111111.222'];

    component.filteredHistory = expectFilteredHistories;
    component.onMouseClick(selectedEntryIndex);
    fixture.detectChanges();

    expect(component.inputConfig.value).toEqual(expectFilteredHistories[1]);
  });

  it('should show expected filteredHistory when dispatch keyup event', () => {
    let expectFilteredHistory = ['3333', '33.11'];

    let input = debugElement.query(By.css('input'));
    let inputElement = input.nativeElement;

    component.inputConfig.value = '3';
    (component as any).history = ['3333', '1111', '44', '33.11'];
    inputElement.dispatchEvent(new KeyboardEvent('keyup'));
    fixture.detectChanges();

    expect(component.filteredHistory).toEqual(expectFilteredHistory);
  });

  describe('historyItemIndex', () => {
    it('should set historyItemIndex to "-1" when the event key is invalid e.g. "Up"', () => {
      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'Up' }));
      fixture.detectChanges();

      expect(component.historyItemIndex).toEqual(-1);
    });

    it('should add 1 to historyItemIndex when press ArrowDown', () => {
      let expectedFilteredHistory = ['12345', '131313', '1111'];

      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      (component as any).history = ['12345', '44', '3311', '131313', '1111'];
      component.inputConfig.value = '1';
      component.onFocus();
      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown' }));
      fixture.detectChanges();

      expect(component.filteredHistory).toEqual(expectedFilteredHistory);
      expect(component.historyItemIndex).toEqual(0);

      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown' }));
      fixture.detectChanges();

      expect(component.historyItemIndex).toEqual(1);
    });

    it('should minus 1 to historyItemIndex when press ArrowUp', () => {
      let expectedFilteredHistory = ['33333', '3311', '313131'];

      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      (component as any).history = ['33333', '1111', '3311', '313131', '565656'];
      component.inputConfig.value = '3';
      component.historyItemIndex = 2;
      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowUp' }));
      fixture.detectChanges();

      expect(component.filteredHistory).toEqual(expectedFilteredHistory);
      expect(component.historyItemIndex).toEqual(1);

      // set historyItemIndex to 'filteredHistory.length - 1' when historyItemIndex < 0
      component.historyItemIndex = 0;
      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowUp' }));
      fixture.detectChanges();

      let expectedIndex = component.filteredHistory.length - 1;
      expect(component.historyItemIndex).toEqual(expectedIndex);
    });

    it('should set historyItemIndex to "0" when historyItemIndex greater than the length of filteredHistory', () => {
      let input = debugElement.query(By.css('input'));
      let inputElement = input.nativeElement;

      (component as any).history = ['511', '1111', '511', '554433', '33333'];
      component.inputConfig.value = '5';
      component.historyItemIndex = 3;
      inputElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown' }));
      fixture.detectChanges();

      expect(component.filteredHistory.length).toEqual(3);
      expect(component.historyItemIndex).toEqual(0);
    });
  });
});
