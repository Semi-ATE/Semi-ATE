import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { expectWaitUntil } from 'src/app/test-stuff/auxillary-test-functions';
import { Alignment, generateTableEntry } from './table-config';
import { TableComponent } from './table.component';

describe('TableComponent', () => {
  let component: TableComponent;
  let fixture: ComponentFixture<TableComponent>;
  let debugElement: DebugElement;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TableComponent);
    component = fixture.componentInstance;
    debugElement = fixture.debugElement;
    fixture.detectChanges();
  });

  const tableHeaders = [
    {
      text: '',
      align: undefined,
      textColor: undefined,
      backgroundColor: undefined
    },
    {
      text: 'Header 1',
      align: Alignment.Center,
      textColor: 'black',
      backgroundColor: 'blue'
    },
  ];

  const tableRows = [[
    {
      text: 'Row 1-1',
      align: Alignment.Center,
      textColor: 'black',
      backgroundColor: 'white'
    },
    {
      text: 'Row 1-2',
      align: Alignment.Center,
      textColor: 'red',
      backgroundColor: 'black'
    }
  ]];

  function arraysOfStringsAreEqual(first: Array<string>, second: Array<string>): boolean {
    let key1 = first?.reduce((a,c) => a + '_' + c, '');
    let key2 = second?.reduce((a,c) => a + '_' + c, '');
    return key1 === key2;
  }

  it('should create table component', () => {
    expect(component).toBeTruthy();
  });

  it('should support table header and rows', () => {
    component.tableConfig.initTable(
      [generateTableEntry('header'), generateTableEntry('header')],
      [
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
        [generateTableEntry('entry'), generateTableEntry('entry')],
      ]
    );
    fixture.detectChanges();

    let tableHeaderElement = debugElement.queryAll(By.css('.tableHeader li'));
    let tableRowElement = debugElement.queryAll(By.css('.tableRow li'));

    expect(tableHeaderElement.length).toBeGreaterThan(0);
    expect(tableRowElement.length).toBeGreaterThan(0);
  });

  describe('Table Headers', () => {
    it('should support text', () => {
      const expectedHeaderTexts = ['', 'Header 1'];
      component.tableConfig.headerRow = tableHeaders;
      fixture.detectChanges();

      let tableHeaderLabels = debugElement.queryAll(By.css('.tableHeader li')).map(e => e.nativeElement.innerText);
      expect(tableHeaderLabels).toEqual(expectedHeaderTexts);
    });

    it('should support backgroundColor', async () => {
      const expectedBackgroundColor = 'red';
      component.tableConfig.headerRow = tableHeaders;
      fixture.detectChanges();

      let tableheaderElement = debugElement.query(By.css('.tableHeader li')).nativeElement;
      expect(tableheaderElement.getAttribute('style').backgroundColor).toEqual(undefined);

      component.tableConfig.headerRow[0].backgroundColor = 'red';

      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => tableheaderElement.style.backgroundColor === expectedBackgroundColor,
        'Element can not get expected background color'
      );
    });
  });

  describe('Table Rows', () => {
    it('should support texts', () => {
      const expectedRowEntryTexts = ['Row 1-1', 'Row 1-2'];
      component.tableConfig.rows = tableRows;
      fixture.detectChanges();

      let tableRowEntry = debugElement.queryAll(By.css('.tableRow li')).map(e => e.nativeElement.innerText);
      expect(tableRowEntry).toEqual(expectedRowEntryTexts);
    });

    it('should support styles', () => {
      const defaultRowEntryStyle = 'display: block; color: black; text-align: center; background-color: white';
      const expectedRowEntryStyle = 'color: blue; text-align: left; background-color: rgb(221, 221, 221)';
      component.tableConfig.rows = tableRows;
      fixture.detectChanges();

      let tableRowEntryElement = debugElement.query(By.css('.tableRow li')).nativeElement;
      expect(tableRowEntryElement.getAttribute('style')).toContain(defaultRowEntryStyle);

      component.tableConfig.rows[0][0].align = Alignment.Left;
      component.tableConfig.rows[0][0].backgroundColor = '#ddd';
      component.tableConfig.rows[0][0].textColor = 'blue';
      fixture.detectChanges();

      expect(tableRowEntryElement.getAttribute('style')).toContain(expectedRowEntryStyle);
    });
  });

  describe('initTable', () => {
    it('should support array of width', async () => {
      const expectedWidths = ['30%', '50%'];
      component.tableConfig.initTable(tableHeaders, tableRows, expectedWidths);
      fixture.detectChanges();

      let firstTableEntries = debugElement.query(By.css('.tableRow')).queryAll(By.css('li'));
      let widthOfFirstTableEntries = firstTableEntries.map(e => e.nativeElement.style.width);
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => arraysOfStringsAreEqual(widthOfFirstTableEntries, expectedWidths),
        'Expected CSS width was not found'
      );
    });

    it('should compute width array automatically if not provided', async () => {
      const expectedWidths = ['50%', '50%'];
      component.tableConfig.initTable(undefined, [[generateTableEntry('entry 1'), generateTableEntry('entry 2')]]);
      fixture.detectChanges();

      let firstTableEntries = debugElement.query(By.css('.tableRow')).queryAll(By.css('li'));
      let widthOfFirstTableEntries = firstTableEntries.map(e => e.nativeElement.style.width);
      await expectWaitUntil(
        () => fixture.detectChanges(),
        () => arraysOfStringsAreEqual(widthOfFirstTableEntries, expectedWidths),
        'Expected CSS width was not found'
      );
    });

    it('should display an error message when the table row entry is empty', async () => {
      const expectedWidths = ['30%', '70%'];
      const expectedRowEntry = [];
      const expectedErrorMessage = 'Length of array containing width informations has to be equal to the number of columns';

      expect(() => {
        component.tableConfig.initTable(undefined, expectedRowEntry, expectedWidths);
        fixture.detectChanges();
      }).toThrow(new Error(expectedErrorMessage));
    });
  });
});
