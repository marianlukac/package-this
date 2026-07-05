import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';
import { PackageListItem, PackageStatus, STATUS_LABELS } from '../../models/package.model';

@Component({
  selector: 'app-package-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h1 class="text-2xl font-bold text-gray-900">Packages</h1>
        <div class="flex items-center gap-2">
          <button class="btn-secondary text-xs" (click)="resetToPersonaDefaults()">
            Reset to My View
          </button>
          <a routerLink="/sales/new" class="btn-primary">+ New Sale</a>
        </div>
      </div>

      <!-- Search -->
      <div class="card flex flex-wrap gap-3 items-end">
        <div class="flex-1 min-w-48">
          <label class="label" for="search">Search</label>
          <input
            id="search"
            type="text"
            class="input w-full"
            placeholder="Package ID, customer, or contents…"
            [(ngModel)]="searchTerm"
            (input)="onSearch()"
            aria-label="Search packages"
          />
        </div>
        <div>
          <label class="label" for="filter-status">Status</label>
          <select id="filter-status" class="input w-40" [(ngModel)]="filterStatus" (change)="load()">
            <option value="">All statuses</option>
            @for (entry of statusOptions; track entry.value) {
              <option [value]="entry.value">{{ entry.label }}</option>
            }
          </select>
        </div>
        <div>
          <label class="label" for="filter-priority">Priority</label>
          <select id="filter-priority" class="input w-32" [(ngModel)]="filterPriority" (change)="load()">
            <option value="">All</option>
            <option value="standard">Standard</option>
            <option value="express">Express</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div>
          <label class="label" for="filter-delayed">Delays</label>
          <select id="filter-delayed" class="input w-32" [(ngModel)]="filterHasDelay" (change)="load()">
            <option value="">All</option>
            <option value="true">Delayed only</option>
            <option value="false">No delays</option>
          </select>
        </div>
        <div>
          <label class="label" for="filter-exception">Exception</label>
          <select id="filter-exception" class="input w-36" [(ngModel)]="filterException" (change)="load()">
            <option value="">None</option>
            <option value="damaged">Damaged</option>
            <option value="cancelled">Cancelled</option>
            <option value="returned">Returned</option>
            <option value="any">Any exception</option>
          </select>
        </div>
        <div>
          <label class="label" for="sort-by">Sort</label>
          <select id="sort-by" class="input w-40" [(ngModel)]="sortBy" (change)="load()">
            <option value="">Last Updated</option>
            <option value="expected_delivery">Expected Delivery</option>
            <option value="priority">Priority</option>
          </select>
        </div>
        <button class="btn-secondary" (click)="clearFilters()">Clear</button>
      </div>

      <!-- Table -->
      @if (loading) {
        <div class="card py-8">
          <div class="animate-pulse space-y-3">
            @for (i of [1,2,3,4,5]; track i) {
              <div class="h-10 bg-gray-100 rounded"></div>
            }
          </div>
        </div>
      } @else if (errorMsg) {
        <div class="card text-center py-8">
          <p class="text-red-600 font-medium">{{ errorMsg }}</p>
          <button class="btn-secondary mt-3 text-xs" (click)="load()">Try again</button>
        </div>
      } @else if (packages.length === 0) {
        <div class="card text-center py-12 text-gray-400">
          <p class="text-lg">No packages found</p>
          <p class="text-sm mt-1">Adjust filters or create a new sale</p>
        </div>
      } @else {
        <div class="card p-0 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200" role="grid" aria-label="Package list">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Package ID</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium uppercase"
                      [class.text-dm-blue]="isAccounting || isSales"
                      [class.text-gray-500]="!isAccounting && !isSales">Customer</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Salesperson</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium uppercase"
                      [class.text-dm-blue]="isAccounting"
                      [class.text-gray-500]="!isAccounting">Invoice Creator</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Delay</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium uppercase"
                      [class.text-dm-blue]="isWarehouse"
                      [class.text-gray-500]="!isWarehouse">Truck</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 bg-white">
                @for (pkg of packages; track pkg.package_id) {
                  <tr
                    class="hover:bg-gray-50 cursor-pointer"
                    [class.bg-orange-50]="isAccounting && isTerminalStatus(pkg.status)"
                    role="row"
                  >
                    <td class="px-3 py-2.5 text-sm">
                      <a [routerLink]="['/packages', pkg.package_id]"
                         class="font-medium text-dm-blue hover:underline focus:underline focus:outline-none"
                         [attr.aria-label]="'View package ' + pkg.package_id">
                        {{ pkg.package_id }}
                      </a>
                    </td>
                    <td class="px-3 py-2.5 text-sm"
                        [class.font-semibold]="isSales"
                        [class.text-gray-900]="isSales">
                      {{ pkg.customer_name }}
                    </td>
                    <td class="px-3 py-2.5 text-sm text-gray-600">{{ pkg.salesperson_name }}</td>
                    <td class="px-3 py-2.5 text-sm"
                        [class.font-semibold]="isAccounting"
                        [class.text-gray-900]="isAccounting">
                      {{ pkg.invoicing_employee_name ?? pkg.invoice_id }}
                    </td>
                    <td class="px-3 py-2.5">
                      <span [class]="'status-' + pkg.status" role="status">{{ statusLabel(pkg.status) }}</span>
                    </td>
                    <td class="px-3 py-2.5 text-xs">
                      @if (pkg.delay_reason) {
                        <span class="badge bg-orange-100 text-orange-700" [title]="pkg.delay_reason">⚠ Delayed</span>
                      }
                    </td>
                    <td class="px-3 py-2.5 text-xs"
                        [class.font-semibold]="isWarehouse"
                        [class.text-teal-700]="isWarehouse && pkg.truck_id">
                      {{ pkg.truck_id ?? '—' }}
                    </td>
                    <td class="px-3 py-2.5 text-xs text-gray-500 max-w-32 truncate">{{ pkg.current_location ?? '—' }}</td>
                    <td class="px-3 py-2.5 text-xs text-gray-500">{{ pkg.updated_at | date:'short' }}</td>
                    <td class="px-3 py-2.5">
                      <span [class]="'priority-' + pkg.priority">{{ pkg.priority }}</span>
                    </td>
                    <td class="px-3 py-2.5 text-xs">
                      @if (pkg.fragile) {
                        <span class="badge bg-yellow-100 text-yellow-700">🔺 Fragile</span>
                      }
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
          <!-- Pagination -->
          <div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-sm text-gray-500">
            <span>Showing {{ packages.length }} of {{ total }}</span>
            <div class="flex gap-2">
              <button class="btn-secondary text-xs" [disabled]="offset === 0" (click)="prevPage()">← Previous</button>
              <button class="btn-secondary text-xs" [disabled]="offset + limit >= total" (click)="nextPage()">Next →</button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
})
export class PackageListComponent implements OnInit {
  private api = inject(ApiService);
  private persona = inject(PersonaService);
  private route = inject(ActivatedRoute);

  protected packages: PackageListItem[] = [];
  protected total = 0;
  protected loading = true;
  protected errorMsg = '';

  // Filters
  protected searchTerm = '';
  protected filterStatus = '';
  protected filterPriority = '';
  protected filterHasDelay = '';
  protected filterException = '';
  protected sortBy = '';
  protected limit = 25;
  protected offset = 0;

  protected statusOptions = Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }));

  get isManager(): boolean { return this.persona.isManager(); }
  get isSales(): boolean { return this.persona.isSales(); }
  get isAccounting(): boolean { return this.persona.isAccounting(); }
  get isWarehouse(): boolean { return this.persona.isWarehouse(); }

  ngOnInit(): void {
    // Apply query-param pre-filters (e.g. from status-card click)
    this.route.queryParams.subscribe(params => {
      if (params['status']) this.filterStatus = params['status'];
      if (params['salesperson_id']) {
        // Handled via persona defaults
      }
      this.applyPersonaDefaults();
      this.load();
    });
  }

  private applyPersonaDefaults(): void {
    if (this.filterStatus) return; // query param wins
    const roleGroup = this.persona.getRoleGroup();
    if (roleGroup === 'sales') {
      // Sales: pre-filter handled via salesperson_id in params
    }
    // Warehouse: no default status filter — they see all, with emphasis
    // Others: no default filter
  }

  resetToPersonaDefaults(): void {
    this.clearFilters();
    // Sales persona: filter to own packages
    if (this.isSales) {
      this.load({ salesperson_id: this.persona.currentPersonaId() });
      return;
    }
    if (this.isWarehouse) {
      this.filterStatus = '';
      this.sortBy = '';
    }
    this.load();
  }

  load(extra?: Record<string, string | number | boolean>): void {
    this.loading = true;
    this.errorMsg = '';

    const params: Record<string, string | number | boolean> = {
      limit: this.limit,
      offset: this.offset,
    };

    if (this.filterStatus) params['status'] = this.filterStatus;
    if (this.filterPriority) params['priority'] = this.filterPriority;
    if (this.filterHasDelay) params['has_delay'] = this.filterHasDelay === 'true';
    if (this.filterException) params['exception_state'] = this.filterException;
    if (this.searchTerm.trim()) params['search'] = this.searchTerm.trim();
    if (this.sortBy) params['sort_by'] = this.sortBy;

    if (extra) Object.assign(params, extra);

    this.api.getPackages(params as any).subscribe({
      next: (res) => {
        this.packages = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMsg = 'Could not load your packages. Please try again.';
      },
    });
  }

  private searchTimeout: ReturnType<typeof setTimeout> | null = null;

  onSearch(): void {
    if (this.searchTimeout) clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.offset = 0;
      this.load();
    }, 300);
  }

  statusLabel(status: PackageStatus): string {
    return STATUS_LABELS[status] ?? status;
  }

  isTerminalStatus(status: string): boolean {
    return ['cancelled', 'damaged', 'returned'].includes(status);
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.filterStatus = '';
    this.filterPriority = '';
    this.filterHasDelay = '';
    this.filterException = '';
    this.sortBy = '';
    this.offset = 0;
    this.load();
  }

  prevPage(): void {
    this.offset = Math.max(0, this.offset - this.limit);
    this.load();
  }

  nextPage(): void {
    this.offset += this.limit;
    this.load();
  }
}
