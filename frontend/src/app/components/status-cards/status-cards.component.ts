import { Component, Input, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { OperationalSummary } from '../../models/sale.model';
import { ApiService } from '../../services/api.service';
import { PackageStatus } from '../../models/package.model';

const ALL_STATUSES: PackageStatus[] = [
  'order_created', 'backorder', 'packaged', 'ready_for_shipping',
  'shipped', 'in_transit', 'delivered', 'cancelled', 'damaged', 'returned',
];

const TERMINAL: Set<string> = new Set(['delivered', 'cancelled', 'damaged', 'returned']);

const STATUS_DISPLAY: Record<string, { label: string; color: string }> = {
  order_created:     { label: 'Order Created',   color: 'text-gray-600' },
  backorder:         { label: 'Backorder',        color: 'text-yellow-600' },
  packaged:          { label: 'Packaged',         color: 'text-blue-600' },
  ready_for_shipping:{ label: 'Ready to Ship',    color: 'text-teal-600' },
  shipped:           { label: 'Shipped',          color: 'text-purple-600' },
  in_transit:        { label: 'In Transit',       color: 'text-indigo-600' },
  delivered:         { label: 'Delivered',        color: 'text-green-600' },
  cancelled:         { label: 'Cancelled',        color: 'text-gray-400' },
  damaged:           { label: 'Damaged',          color: 'text-red-600' },
  returned:          { label: 'Returned',         color: 'text-red-400' },
};

@Component({
  selector: 'app-status-cards',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2"
         role="region" aria-label="Package status overview">
      @for (status of allStatuses; track status) {
        <a
          routerLink="/packages"
          [queryParams]="{status: status}"
          class="card p-3 text-center hover:shadow transition-shadow focus:outline-none focus:ring-2 cursor-pointer"
          [class.border-red-100]="isTerminal(status)"
          [class.bg-red-50]="isTerminal(status)"
          [class.hover:border-red-300]="isTerminal(status)"
          [class.focus:ring-red-300]="isTerminal(status)"
          [class.hover:border-dm-blue]="!isTerminal(status)"
          [class.focus:ring-dm-blue]="!isTerminal(status)"
          [attr.aria-label]="getCount(status) + ' packages with status ' + getLabel(status)"
          tabindex="0"
        >
          <div class="text-xl font-bold" [ngClass]="getColor(status)">{{ getCount(status) }}</div>
          <div class="text-xs text-gray-500 mt-0.5 leading-tight">{{ getLabel(status) }}</div>
        </a>
      }
    </div>
  `,
})
export class StatusCardsComponent implements OnInit {
  @Input({ required: true }) summary!: OperationalSummary;
  private api = inject(ApiService);

  protected allStatuses = ALL_STATUSES;
  private counts: Record<string, number> = {};

  ngOnInit(): void {
    // Seed from summary fields immediately
    this.counts['in_transit'] = this.summary.in_transit;
    this.counts['backorder'] = this.summary.backorder_count ?? 0;
    this.counts['order_created'] = this.summary.order_created_count ?? 0;

    // Fetch all packages (capped at 500) to get per-status counts
    this.api.getPackages({ limit: 500 }).subscribe(res => {
      const fresh: Record<string, number> = {};
      for (const pkg of res.items) {
        fresh[pkg.status] = (fresh[pkg.status] ?? 0) + 1;
      }
      this.counts = fresh;
    });
  }

  getCount(status: string): number {
    return this.counts[status] ?? 0;
  }

  getLabel(status: string): string {
    return STATUS_DISPLAY[status]?.label ?? status;
  }

  getColor(status: string): string {
    return STATUS_DISPLAY[status]?.color ?? 'text-gray-600';
  }

  isTerminal(status: string): boolean {
    return TERMINAL.has(status);
  }
}
