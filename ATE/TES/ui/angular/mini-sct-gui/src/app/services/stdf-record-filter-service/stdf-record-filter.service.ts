import { Injectable, OnDestroy } from '@angular/core';
import { StdfRecord } from '../../stdf/stdf-stuff';
import { SdtfRecordFilter, FilterFunction } from './stdf-record-filter';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppstateService } from '../appstate.service';

@Injectable({
  providedIn: 'root'
})
export class StdfRecordFilterService implements OnDestroy {
  resultChanged$: Subject<void>;
  newResultsAvailable$: Subject<void>;
  filteredRecords: StdfRecord[];
  private filters: SdtfRecordFilter[];
  private readonly unsubscribe$: Subject<void>;

  constructor(private readonly appStateService: AppstateService) {
    this.resultChanged$ = new Subject<void>();
    this.newResultsAvailable$ = new Subject<void>();
    this.filteredRecords = [];
    this.filters = [];
    this.unsubscribe$ = new Subject<void>();
    this.appStateService.newRecordReceived$
      .pipe(takeUntil(this.unsubscribe$))
      .subscribe({next: (newRecords: StdfRecord[]) => this.updateFilteredRecords(newRecords)});
    this.appStateService.rebuildRecords$
      .pipe(takeUntil(this.unsubscribe$))
      .subscribe(
        {
          next: () => {
            this.applyAllFilters();
            this.resultChanged$.next();
            this.newResultsAvailable$.next();
          }
        }
      );
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  registerFilter(filter: Subject<SdtfRecordFilter>): void {
    filter.pipe(takeUntil(this.unsubscribe$)).subscribe(f => this.manageFilterChange(f));
  }

  clearFilters() {
    this.filters = [];
  }

  private updateFilteredRecords(toAdd: StdfRecord[]) {
    let toAddFiltered = toAdd.filter(this.combineActiveFilters());
    this.filteredRecords = this.filteredRecords.concat(toAddFiltered);
    this.newResultsAvailable$.next();
  }

  private manageFilterChange(filter: SdtfRecordFilter) {
    let strengthen = this.addFilter(filter);
    if (strengthen) {
      this.updateByFilter(filter);
    } else {
      this.applyAllFilters();
    }
    this.resultChanged$.next();
  }

  private updateByFilter(filter: SdtfRecordFilter) {
    if (!filter.active)
      throw new Error('Filter must be active in order to strengthen the current result');
    this.filteredRecords = this.filteredRecords.filter(filter.filterFunction);
  }

  private addFilter(filter: SdtfRecordFilter): boolean {
    let filterGetStronger = false;
    let foundFilter = this.filters.find(e => e.type === filter.type);
    if (!foundFilter) {
      this.filters.push(filter);
      filterGetStronger = filter.active && filter.strengthen;
    } else {
      if (!foundFilter.active && filter.active) {
        filterGetStronger = true;
      } else if (foundFilter.active && filter.active && filter.strengthen) {
        filterGetStronger = true;
      }
      foundFilter = filter;
    }
    return filterGetStronger;
  }

  private applyAllFilters() {
    this.filteredRecords = this.appStateService.stdfRecords.filter(this.combineActiveFilters());
  }

  private combineActiveFilters(): FilterFunction {
    let activeFilters = this.filters.filter(f => f.active);
    return activeFilters.reduce( (a,f) => (r:StdfRecord) => a(r) && f.filterFunction(r), (e: StdfRecord) => true);
  }
}
