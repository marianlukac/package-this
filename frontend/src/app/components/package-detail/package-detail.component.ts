import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';
import { Package, TERMINAL_STATUSES, STATUS_LABELS } from '../../models/package.model';
import { PackageHistoryComponent } from '../package-history/package-history.component';
import { LifecycleButtonsComponent } from '../lifecycle-buttons/lifecycle-buttons.component';
import { LineItemManagerComponent } from '../line-item-manager/line-item-manager.component';
import { DelayDialogComponent } from '../delay-dialog/delay-dialog.component';
import { ManagerActionDialogComponent } from '../manager-action-dialog/manager-action-dialog.component';
import { PersonaUnavailableComponent } from '../persona-unavailable/persona-unavailable.component';

@Component({
  selector: 'app-package-detail',
  standalone: true,
  imports: [
    CommonModule, RouterLink,
    PackageHistoryComponent, LifecycleButtonsComponent,
    LineItemManagerComponent, DelayDialogComponent, ManagerActionDialogComponent,
    PersonaUnavailableComponent,
  ],
  template: `
    <div class="space-y-5">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <a routerLink="/packages" class="text-xs text-dm-blue hover:underline">← All Packages</a>
          <h1 class="text-2xl font-bold text-gray-900 mt-1">{{ pkg?.package_id }}</h1>
          <p class="text-sm text-gray-500">{{ pkg?.customer_name }} · Sale {{ pkg?.sale_id }}</p>
        </div>
        @if (pkg) {
          <div class="flex items-center gap-2 flex-wrap">
            <span [class]="'status-' + pkg.status" [attr.aria-label]="'Status: ' + pkg.status">
              {{ statusLabel(pkg.status) }}
            </span>
            <span [class]="'priority-' + pkg.priority">{{ pkg.priority }}</span>
            @if (pkg.fragile) {
              <span class="badge bg-yellow-100 text-yellow-700">🔺 Fragile</span>
            }
            @if (pkg.delay_reason) {
              <span class="badge bg-orange-100 text-orange-700" [title]="pkg.delay_reason">⚠ Delayed</span>
            }
          </div>
        }
      </div>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading…</p>
      } @else if (!pkg) {
        <div class="card text-center py-12 text-gray-400">Package not found.</div>
      } @else {
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <!-- Left: Package info + line items -->
          <div class="lg:col-span-2 space-y-4">
            <!-- Details card -->
            <div class="card">
              <h2 class="font-semibold text-gray-800 mb-3">Package Details</h2>
              <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <dt class="text-gray-500">Customer</dt>
                <dd class="text-gray-900">{{ pkg.customer_name }}</dd>
                <dt class="text-gray-500">Salesperson</dt>
                <dd>{{ pkg.salesperson_name }}</dd>
                <dt class="text-gray-500">Invoice</dt>
                <dd>{{ pkg.invoicing_employee_name }}</dd>
                <dt class="text-gray-500">Destination</dt>
                <dd>{{ pkg.destination ?? '—' }}</dd>
                <dt class="text-gray-500">Location</dt>
                <dd>{{ pkg.current_location ?? '—' }}</dd>
                <dt class="text-gray-500">Truck</dt>
                <dd>{{ pkg.truck_id ?? '—' }}</dd>
                <dt class="text-gray-500">Expected Delivery</dt>
                <dd>{{ pkg.expected_delivery ? (pkg.expected_delivery | date:'medium') : '—' }}</dd>
                <dt class="text-gray-500">Contents</dt>
                <dd>{{ pkg.contents_summary ?? '—' }}</dd>
                @if (pkg.delay_reason) {
                  <dt class="text-orange-600">Delay Reason</dt>
                  <dd class="text-orange-700">{{ pkg.delay_reason }} ({{ pkg.delay_duration_hours }}h)</dd>
                }
                <dt class="text-gray-500">Created</dt>
                <dd>{{ pkg.created_at | date:'medium' }}</dd>
                <dt class="text-gray-500">Updated</dt>
                <dd>{{ pkg.updated_at | date:'medium' }}</dd>
              </dl>
            </div>

            <!-- Line items -->
            <app-line-item-manager
              [package]="pkg"
              [isTerminal]="isTerminal"
              (changed)="reload()"
            />

            <!-- Actions -->
            @if (!isTerminal) {
              <div class="card space-y-3">
                <h2 class="font-semibold text-gray-800">Actions</h2>

                <!-- Lifecycle buttons: warehouse and manager only -->
                @if (persona.isWarehouse() || persona.isManager()) {
                  <app-lifecycle-buttons [pkg]="pkg" (changed)="reload()" />
                } @else {
                  <app-persona-unavailable
                    action="Advance Lifecycle"
                    requiredRole="warehouse or manager"
                  />
                }

                <!-- Record delay: warehouse and manager only -->
                @if (persona.isWarehouse() || persona.isManager()) {
                  <button class="btn-warning text-xs" (click)="showDelay = true">Record Delay</button>
                } @else {
                  <app-persona-unavailable
                    action="Record Delay"
                    requiredRole="warehouse or manager"
                  />
                }

                <!-- Manager actions: manager only -->
                @if (persona.isManager()) {
                  <button class="btn-secondary text-xs" (click)="showManagerAction = true">Manager Action</button>
                } @else {
                  <app-persona-unavailable
                    action="Manager Action"
                    requiredRole="manager"
                  />
                }

                <!-- Complaint: sales and up -->
                @if (!persona.isWarehouse()) {
                  <a routerLink="/complaints" class="text-xs text-dm-blue hover:underline">+ Create Complaint</a>
                }
              </div>
            } @else {
              <div class="card bg-gray-50 text-center text-sm text-gray-500 py-4">
                <span class="font-medium text-gray-700">Terminal status: {{ pkg.status }}</span>
                <p class="mt-1">No further lifecycle changes allowed for this package.</p>
              </div>
            }
          </div>

          <!-- Right: History -->
          <div>
            <app-package-history [packageId]="pkg.package_id" />
          </div>
        </div>

        @if (showDelay) {
          <app-delay-dialog [packageId]="pkg.package_id" (closed)="onDelayClose($event)" />
        }
        @if (showManagerAction) {
          <app-manager-action-dialog [entityId]="pkg.package_id" [entityType]="'package'"
                                     (closed)="onManagerActionClose($event)" />
        }
      }
    </div>
  `,
})
export class PackageDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);
  protected persona = inject(PersonaService);
  protected pkg: Package | null = null;
  protected loading = true;
  protected showDelay = false;
  protected showManagerAction = false;

  get isTerminal(): boolean {
    return !!this.pkg && TERMINAL_STATUSES.includes(this.pkg.status);
  }

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    this.loading = true;
    this.showDelay = false;
    this.showManagerAction = false;
    this.api.getPackage(id).subscribe({
      next: (pkg) => { this.pkg = pkg; this.loading = false; },
      error: () => { this.pkg = null; this.loading = false; },
    });
  }

  statusLabel(status: string): string {
    return STATUS_LABELS[status as keyof typeof STATUS_LABELS] ?? status;
  }

  onDelayClose(changed: boolean): void {
    this.showDelay = false;
    if (changed) this.reload();
  }

  onManagerActionClose(changed: boolean): void {
    this.showManagerAction = false;
    if (changed) this.reload();
  }
}
