import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Package, PackageStatus } from '../../models/package.model';

const NEXT_STATUS: Partial<Record<PackageStatus, PackageStatus>> = {
  order_created: 'packaged',
  backorder: 'packaged',
  packaged: 'ready_for_shipping',
  ready_for_shipping: 'shipped',
  shipped: 'in_transit',
  in_transit: 'delivered',
};

const NEXT_LABEL: Partial<Record<PackageStatus, string>> = {
  order_created: 'Mark Packaged',
  backorder: 'Mark Packaged',
  packaged: 'Ready for Shipping',
  ready_for_shipping: 'Mark Shipped',
  shipped: 'Mark In Transit',
  in_transit: 'Mark Delivered',
};

@Component({
  selector: 'app-lifecycle-buttons',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-2">
      @if (nextStatus) {
        <div class="flex items-center gap-2 flex-wrap">
          <button
            class="btn-primary text-xs"
            [disabled]="busy"
            (click)="advance()"
            [attr.aria-label]="nextLabel"
          >
            {{ nextLabel }}
          </button>
          <input class="input text-xs w-48" [(ngModel)]="reason" placeholder="Reason (optional)"
                 aria-label="Reason for status change" />
        </div>
      }

      <!-- Terminal exception buttons -->
      <div class="flex gap-2 flex-wrap">
        <button class="btn-danger text-xs" [disabled]="busy"
                (click)="advanceTo('cancelled')" aria-label="Cancel package">
          Cancel
        </button>
        <button class="btn-danger text-xs" [disabled]="busy"
                (click)="advanceTo('damaged')" aria-label="Mark as damaged">
          Mark Damaged
        </button>
        @if (pkg.status === 'in_transit' || pkg.status === 'delivered') {
          <button class="btn-warning text-xs" [disabled]="busy"
                  (click)="advanceTo('returned')" aria-label="Mark as returned">
            Mark Returned
          </button>
        }
      </div>

      @if (errorMsg) {
        <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
      }
    </div>
  `,
})
export class LifecycleButtonsComponent {
  @Input({ required: true }) pkg!: Package;
  @Output() changed = new EventEmitter<void>();

  private api = inject(ApiService);
  protected reason = '';
  protected busy = false;
  protected errorMsg = '';

  get nextStatus(): PackageStatus | undefined {
    return NEXT_STATUS[this.pkg.status];
  }

  get nextLabel(): string {
    return NEXT_LABEL[this.pkg.status] ?? '';
  }

  advance(): void {
    if (!this.nextStatus) return;
    this.advanceTo(this.nextStatus);
  }

  advanceTo(status: PackageStatus): void {
    this.busy = true;
    this.errorMsg = '';
    this.api.advanceStatus(this.pkg.package_id, status, this.reason || undefined).subscribe({
      next: () => { this.busy = false; this.reason = ''; this.changed.emit(); },
      error: (err) => {
        this.busy = false;
        if (err.status === 409) {
          this.errorMsg = err.error?.detail ?? 'Invalid transition.';
        } else if (err.status === 403) {
          this.errorMsg = 'You do not have permission for this action.';
        } else {
          this.errorMsg = 'An error occurred.';
        }
      },
    });
  }
}
