import { Component, Input, OnChanges, OnInit, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';
import { TruckRoute, TruckDetail, ViaPoint } from '../../models/truck.model';
import { MapLocation } from '../../models/map.model';

@Component({
  selector: 'app-truck-route-view',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div
      class="card text-sm"
      role="dialog"
      aria-labelledby="route-panel-title"
      (keydown.escape)="close()">
      <div class="flex items-center justify-between mb-3">
        <h2 id="route-panel-title" class="font-semibold text-gray-800">
          {{ detail?.name ?? truckId }}
        </h2>
        <button
          class="text-gray-400 hover:text-gray-600 text-lg leading-none"
          (click)="close()"
          aria-label="Close route panel">×</button>
      </div>

      @if (!route) {
        <p class="text-xs text-gray-400">No active route — truck is at warehouse.</p>
      } @else {
        <!-- Route summary -->
        <div class="flex flex-wrap gap-1 mb-3">
          <span [class]="statusBadge(route.status)">{{ route.status }}</span>
          @if (detail?.delay_reason) {
            <span class="badge bg-orange-100 text-orange-700">⚠ {{ detail!.delay_reason }}</span>
          }
          <span class="badge bg-gray-100 text-gray-500">~{{ route.estimated_duration_minutes }} min</span>
        </div>

        <!-- Stop list -->
        <ol class="relative border-l border-gray-200 space-y-2 mb-4" aria-label="Route stops">
          @for (stop of route.stops; track stop.stop_id) {
            <li class="ml-4">
              <span
                class="absolute -left-1.5 flex h-3 w-3 items-center justify-center rounded-full"
                [class]="stop.is_completed ? 'bg-green-200 border border-green-400' : 'bg-white border border-gray-300'"
                aria-hidden="true">
              </span>
              <div>
                <span class="font-medium text-gray-800" [attr.aria-label]="'Stop ' + stop.stop_order + ': ' + stop.customer_name">
                  {{ stop.stop_order }}. {{ stop.customer_name }}
                </span>
                @if (stop.is_completed) {
                  <span class="badge bg-green-100 text-green-700 ml-1" aria-label="Delivered">✓</span>
                }
                <!-- Packages for this stop -->
                @for (pkg of packagesForStop(stop.customer_id); track pkg.package_id) {
                  <div class="text-xs text-gray-400 ml-2">→ {{ pkg.package_id }} ({{ pkg.status }})</div>
                }
              </div>
            </li>
          }
        </ol>

        <!-- Via points -->
        @if (route.via_points.length > 0) {
          <div class="mb-4">
            <h3 class="text-xs font-medium text-orange-700 mb-1">Kevin Reroutes</h3>
            <ul class="space-y-1" aria-label="Reroute via-points">
              @for (vp of route.via_points; track vp.id) {
                <li class="text-xs text-gray-600 flex gap-1" [attr.aria-label]="'Via ' + vp.name + ': ' + vp.reason">
                  <span class="text-orange-500">🍩</span>
                  <span class="font-medium">{{ vp.name }}</span>
                  <span class="text-gray-400">— {{ vp.reason }}</span>
                </li>
              }
            </ul>
          </div>
        }

        <!-- Kevin Reroute button (manager only) -->
        @if (canReroute && !showRerouteForm) {
          <button
            class="btn btn-secondary text-xs w-full"
            (click)="openReroute()"
            aria-label="Trigger Kevin hunger reroute for this truck">
            🍩 Kevin Hunger Reroute
          </button>
        }

        <!-- Reroute form -->
        @if (showRerouteForm) {
          <div
            class="bg-orange-50 rounded-lg p-3 border border-orange-200 space-y-2"
            role="region"
            aria-label="Kevin hunger reroute form">
            <h3 class="font-medium text-orange-800 text-xs">Select detour destination</h3>

            <select
              class="w-full text-xs border border-gray-300 rounded p-1"
              [(ngModel)]="selectedLocationId"
              [attr.aria-label]="'Choose food or donut location for reroute'">
              <option [ngValue]="null">-- Choose location --</option>
              @for (loc of foodLocations; track loc.id) {
                <option [ngValue]="loc.id">🍔 {{ loc.name }}</option>
              }
              @for (loc of donutLocations; track loc.id) {
                <option [ngValue]="loc.id">🍩 {{ loc.name }}</option>
              }
            </select>

            <input
              class="w-full text-xs border border-gray-300 rounded p-1"
              type="text"
              placeholder="Reason (e.g. driver hungry)"
              [(ngModel)]="rerouteReason"
              aria-label="Reroute reason">

            <div class="flex gap-2">
              <button
                class="btn btn-primary text-xs flex-1"
                [disabled]="!selectedLocationId || !rerouteReason"
                (click)="submitReroute()"
                aria-label="Submit reroute">
                Confirm Reroute
              </button>
              <button
                class="btn btn-secondary text-xs"
                (click)="cancelReroute()"
                aria-label="Cancel reroute">
                Cancel
              </button>
            </div>

            @if (rerouteError) {
              <p class="text-xs text-red-600" role="alert">{{ rerouteError }}</p>
            }
          </div>
        }
      }
    </div>
  `,
})
export class TruckRouteViewComponent implements OnChanges {
  @Input({ required: true }) truckId!: string;
  @Output() rerouted = new EventEmitter<void>();

  private api = inject(ApiService);
  private persona = inject(PersonaService);

  protected route: TruckRoute | null = null;
  protected detail: TruckDetail | null = null;
  protected foodLocations: MapLocation[] = [];
  protected donutLocations: MapLocation[] = [];
  protected showRerouteForm = false;
  protected selectedLocationId: number | null = null;
  protected rerouteReason = '';
  protected rerouteError = '';

  get canReroute(): boolean {
    return this.persona.isManager();
  }

  ngOnChanges(): void {
    if (this.truckId) {
      this.loadRoute();
      this.loadDetail();
    }
  }

  loadRoute(): void {
    this.api.getTruckRoute(this.truckId).subscribe({
      next: (r) => this.route = r,
      error: () => this.route = null,
    });
  }

  loadDetail(): void {
    this.api.getTruck(this.truckId).subscribe({
      next: (d) => this.detail = d,
      error: () => this.detail = null,
    });
  }

  packagesForStop(customerId: string): any[] {
    return (this.detail?.assigned_packages ?? []).filter(p => {
      const stop = this.route?.stops.find(s => s.customer_id === customerId);
      return stop && p.stop_order === stop.stop_order;
    });
  }

  openReroute(): void {
    this.showRerouteForm = true;
    this.rerouteError = '';
    if (!this.foodLocations.length) {
      this.api.getMapLocations().subscribe(locs => {
        this.foodLocations = locs.filter(l => l.location_type === 'food');
        this.donutLocations = locs.filter(l => l.location_type === 'donut');
      });
    }
  }

  cancelReroute(): void {
    this.showRerouteForm = false;
    this.selectedLocationId = null;
    this.rerouteReason = '';
    this.rerouteError = '';
  }

  submitReroute(): void {
    if (!this.selectedLocationId || !this.rerouteReason) return;
    this.rerouteError = '';
    this.api.rerouteTruck(this.truckId, {
      location_id: this.selectedLocationId,
      reason: this.rerouteReason,
    }).subscribe({
      next: () => {
        this.cancelReroute();
        this.loadRoute();
        this.loadDetail();
        this.rerouted.emit();
      },
      error: (err) => {
        this.rerouteError = err.error?.detail ?? 'Reroute failed.';
      },
    });
  }

  close(): void {
    // Parent handles closing via (keydown.escape) propagation
  }

  statusBadge(status: string): string {
    const map: Record<string, string> = {
      active: 'badge bg-teal-100 text-teal-700',
      returning: 'badge bg-blue-100 text-blue-700',
      completed: 'badge bg-green-100 text-green-700',
      planned: 'badge bg-gray-100 text-gray-500',
    };
    return map[status] ?? 'badge bg-gray-100 text-gray-500';
  }
}
