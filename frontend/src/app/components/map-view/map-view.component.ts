import { Component, OnInit, OnDestroy, inject, NgZone, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { MapService } from '../../services/map.service';
import { RealtimeService } from '../../services/realtime.service';
import { Truck } from '../../models/truck.model';
import { MapLocation } from '../../models/map.model';
import { TruckRouteViewComponent } from '../truck-route-view/truck-route-view.component';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-map-view',
  standalone: true,
  imports: [CommonModule, TruckRouteViewComponent],
  template: `
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Delivery Map</h1>
          <p class="text-sm text-gray-500">Scranton, PA · {{ locations.length }} locations · {{ trucks.length }} trucks</p>
        </div>
        @if (selectedTruckId) {
          <button
            class="btn btn-secondary text-xs"
            (click)="clearSelection()"
            aria-label="Close truck detail panel">
            ✕ Close panel
          </button>
        }
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <!-- Map container -->
        <div class="lg:col-span-3">
          <div
            id="azure-map"
            class="w-full h-[520px] rounded-lg border border-gray-200 bg-gray-100 relative"
            role="application"
            aria-label="Interactive delivery map of Scranton, PA showing truck locations, customer stops, and food detour options. Click markers for details.">
            @if (!mapLoaded) {
              <div class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                <div class="text-center">
                  <p class="text-4xl mb-2">🗺️</p>
                  <p>Map loading…</p>
                  <p class="text-xs mt-1 text-gray-300">Set AZURE_MAPS_KEY in environment for live rendering</p>
                  <!-- Fallback: static location list -->
                  <div class="mt-4 text-left max-h-48 overflow-y-auto space-y-1 px-4">
                    @for (loc of locations; track loc.id) {
                      <div class="text-xs text-gray-500 flex gap-2">
                        <span [class]="iconClass(loc)">{{ iconEmoji(loc) }}</span>
                        <span>{{ loc.name }}</span>
                        <span class="text-gray-300">{{ loc.lat | number:'1.4-4' }}, {{ loc.lng | number:'1.4-4' }}</span>
                      </div>
                    }
                  </div>
                </div>
              </div>
            }
          </div>

          <!-- Location legend -->
          <div class="flex gap-4 mt-2 text-xs font-medium" role="list" aria-label="Map legend">
            <span role="listitem" class="text-orange-500">🏢 Warehouse</span>
            <span role="listitem" class="text-blue-500">📦 Customer ({{ customerCount }})</span>
            <span role="listitem" class="text-red-500">🍔 Food ({{ foodCount }})</span>
            <span role="listitem" class="text-purple-500">🍩 Donut ({{ donutCount }})</span>
            <span role="listitem" class="text-amber-500">🚛 Truck</span>
          </div>
        </div>

        <!-- Right panel: trucks + detail -->
        <div class="space-y-3" role="region" aria-label="Truck panel">
          <!-- Truck list -->
          <h2 class="font-semibold text-gray-800 text-sm">Trucks</h2>
          @if (trucks.length === 0) {
            <p class="text-xs text-gray-400">No trucks found.</p>
          } @else {
            @for (truck of trucks; track truck.truck_id) {
              <button
                class="card text-sm w-full text-left cursor-pointer transition-colors"
                [class.ring-2]="selectedTruckId === truck.truck_id"
                [class.ring-orange-400]="selectedTruckId === truck.truck_id"
                (click)="selectTruck(truck)"
                [attr.aria-label]="'Select ' + truck.name + ', status: ' + truck.status"
                [attr.aria-pressed]="selectedTruckId === truck.truck_id">
                <div class="font-medium text-gray-900">{{ truck.name }}</div>
                <div class="text-xs text-gray-500">Truck #{{ truck.truck_number }}</div>
                <div class="mt-1 flex gap-1 flex-wrap">
                  <span [class]="statusBadge(truck.status)">{{ truck.status }}</span>
                  @if (truck.delay_reason) {
                    <span class="badge bg-orange-100 text-orange-700">⚠ Delayed</span>
                  }
                  @if (truck.package_count > 0) {
                    <span class="badge bg-blue-100 text-blue-700">{{ truck.package_count }} pkgs</span>
                  }
                </div>
                @if (truck.current_lat && truck.current_lng) {
                  <div class="text-xs text-gray-400 mt-1 font-mono">
                    {{ truck.current_lat | number:'1.4-4' }}, {{ truck.current_lng | number:'1.4-4' }}
                  </div>
                }
              </button>
            }
          }

          <!-- Route detail panel -->
          @if (selectedTruckId) {
            <app-truck-route-view
              [truckId]="selectedTruckId"
              (rerouted)="onRerouted()"
              class="block">
            </app-truck-route-view>
          }
        </div>
      </div>
    </div>
  `,
})
export class MapViewComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);
  private mapSvc = inject(MapService);
  private realtime = inject(RealtimeService);
  private zone = inject(NgZone);
  private cdr = inject(ChangeDetectorRef);

  protected trucks: Truck[] = [];
  protected locations: MapLocation[] = [];
  protected mapLoaded = false;
  protected selectedTruckId: string | null = null;

  private sub: Subscription | null = null;

  get customerCount(): number { return this.locations.filter(l => l.location_type === 'customer').length; }
  get foodCount(): number { return this.locations.filter(l => l.location_type === 'food').length; }
  get donutCount(): number { return this.locations.filter(l => l.location_type === 'donut').length; }

  ngOnInit(): void {
    this.loadData();
    this.initMap();
    this.sub = this.realtime.events$.subscribe(event => {
      if (event.type === 'truck.location_updated') {
        const { truck_id, lat, lng } = (event.data as any) ?? {};
        this.updateTruckPosition(truck_id, lat, lng);
      } else if (event.type === 'truck.rerouted' || event.type === 'truck.dispatched') {
        this.loadTrucks();
      }
    });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
    this.mapSvc.destroyMap();
  }

  loadData(): void {
    this.loadTrucks();
    this.loadLocations();
  }

  loadTrucks(): void {
    this.api.getTrucks().subscribe(trucks => {
      this.trucks = trucks;
      if (this.mapLoaded) {
        for (const t of trucks) {
          this.mapSvc.addOrUpdateTruckMarker(t);
          if (t.current_route_id && t.status !== 'at_warehouse') {
            this.api.getTruckRoute(t.truck_id).subscribe(route => {
              this.mapSvc.addOrUpdateRoutePolyline(t.truck_id, route);
            });
          } else {
            this.mapSvc.removeRoutePolyline(t.truck_id);
          }
        }
      }
    });
  }

  loadLocations(): void {
    this.api.getMapLocations().subscribe(locs => {
      this.locations = locs;
      if (this.mapLoaded) {
        this.mapSvc.addLocationMarkers(locs);
      }
    });
  }

  private async initMap(): Promise<void> {
    await this.mapSvc.initMap('azure-map');
    this.zone.run(() => {
      this.mapLoaded = this.mapSvc.isLoaded;
      this.cdr.detectChanges();
    });

    if (this.mapLoaded) {
      // Add already-loaded data to map
      if (this.locations.length) this.mapSvc.addLocationMarkers(this.locations);
      for (const t of this.trucks) {
        this.mapSvc.addOrUpdateTruckMarker(t);
      }

      // Handle marker clicks
      this.mapSvc.onMarkerClick((props) => {
        if (props['truckId']) {
          const truck = this.trucks.find(t => t.truck_id === props['truckId']);
          if (truck) this.selectTruck(truck);
        }
      });
    }
  }

  private updateTruckPosition(truckId: string, lat: number, lng: number): void {
    const truck = this.trucks.find(t => t.truck_id === truckId);
    if (truck) {
      truck.current_lat = lat;
      truck.current_lng = lng;
      this.mapSvc.addOrUpdateTruckMarker(truck);
    }
  }

  selectTruck(truck: Truck): void {
    this.selectedTruckId = truck.truck_id;
    if (truck.current_lat && truck.current_lng) {
      this.mapSvc.panTo(truck.current_lat, truck.current_lng);
    }
  }

  clearSelection(): void {
    this.selectedTruckId = null;
  }

  onRerouted(): void {
    this.loadTrucks();
  }

  iconClass(loc: MapLocation): string {
    const map: Record<string, string> = { warehouse: 'text-orange-500', customer: 'text-blue-500', food: 'text-red-500', donut: 'text-purple-500' };
    return map[loc.location_type] ?? '';
  }

  iconEmoji(loc: MapLocation): string {
    const map: Record<string, string> = { warehouse: '🏢', customer: '📍', food: '🍔', donut: '🍩' };
    return map[loc.location_type] ?? '📌';
  }

  statusBadge(status: string): string {
    const map: Record<string, string> = {
      on_route: 'badge bg-teal-100 text-teal-700',
      rerouted: 'badge bg-orange-100 text-orange-700',
      returning: 'badge bg-blue-100 text-blue-700',
      at_warehouse: 'badge bg-gray-100 text-gray-600',
      delayed: 'badge bg-red-100 text-red-700',
    };
    return map[status] ?? 'badge bg-gray-100 text-gray-500';
  }
}
