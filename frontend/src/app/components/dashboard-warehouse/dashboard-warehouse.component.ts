import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';

@Component({
  selector: 'app-dashboard-warehouse',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-5">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Warehouse Dashboard</h1>
        <p class="text-sm text-gray-500 mt-1">
          {{ persona.currentPersonaProfile()?.name }} — {{ persona.currentPersonaProfile()?.role }}
        </p>
      </div>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading...</p>
      } @else {
        <!-- Action counts -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <a routerLink="/packages" [queryParams]="{status: 'packaged'}"
             class="card text-center hover:border-dm-blue transition-colors cursor-pointer">
            <div class="text-2xl font-bold text-dm-blue">{{ packagedCount }}</div>
            <div class="text-xs text-gray-500 mt-1">Packaged</div>
          </a>
          <a routerLink="/packages" [queryParams]="{status: 'ready_for_shipping'}"
             class="card text-center hover:border-teal-400 transition-colors cursor-pointer">
            <div class="text-2xl font-bold text-teal-600">{{ readyCount }}</div>
            <div class="text-xs text-gray-500 mt-1">Ready to Ship</div>
          </a>
          <a routerLink="/packages" [queryParams]="{status: 'in_transit'}"
             class="card text-center hover:border-purple-400 transition-colors cursor-pointer">
            <div class="text-2xl font-bold text-purple-600">{{ inTransitCount }}</div>
            <div class="text-xs text-gray-500 mt-1">In Transit</div>
          </a>
          <a routerLink="/packages" [queryParams]="{status: 'damaged'}"
             class="card text-center hover:border-red-400 transition-colors cursor-pointer">
            <div class="text-2xl font-bold" [class.text-red-600]="damagedCount > 0" [class.text-gray-400]="damagedCount === 0">
              {{ damagedCount }}
            </div>
            <div class="text-xs text-gray-500 mt-1">Damaged</div>
          </a>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <!-- Active Trucks -->
          <div class="card">
            <h2 class="font-semibold text-gray-800 mb-3">Active Trucks</h2>
            @if (trucks.length === 0) {
              <p class="text-sm text-gray-400">All packages are moving — nothing to action right now.</p>
            } @else {
              <div class="space-y-2">
                @for (truck of trucks; track truck.truck_id) {
                  <div class="flex items-center justify-between p-2 rounded border border-gray-100">
                    <div>
                      <span class="text-sm font-medium text-gray-900">{{ truck.truck_id }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ truck.driver_name ?? 'No driver' }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-gray-400">{{ truck.current_location ?? '—' }}</span>
                      <span class="badge"
                            [class.bg-teal-100]="truck.status === 'in_transit'"
                            [class.text-teal-700]="truck.status === 'in_transit'"
                            [class.bg-gray-100]="truck.status !== 'in_transit'"
                            [class.text-gray-600]="truck.status !== 'in_transit'">
                        {{ truck.status }}
                      </span>
                    </div>
                  </div>
                }
              </div>
              <a routerLink="/map" class="mt-2 text-xs text-dm-blue hover:underline block">View map →</a>
            }
          </div>

          <!-- Packages Ready to Ship -->
          <div class="card">
            <h2 class="font-semibold text-gray-800 mb-3">Packages Ready for Action</h2>
            @if (actionablePackages.length === 0) {
              <p class="text-sm text-gray-400">All packages are moving — nothing to action right now.</p>
            } @else {
              <div class="space-y-1.5">
                @for (pkg of actionablePackages.slice(0, 8); track pkg.package_id) {
                  <a [routerLink]="['/packages', pkg.package_id]"
                     class="flex items-center justify-between p-2 rounded border border-gray-100 hover:border-teal-400 hover:bg-teal-50 transition-colors text-sm">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-dm-blue text-xs">{{ pkg.package_id }}</span>
                      @if (pkg.truck_id) {
                        <span class="text-xs font-semibold text-teal-700">🚚 {{ pkg.truck_id }}</span>
                      }
                    </div>
                    <span [class]="'status-' + pkg.status" class="text-xs">{{ pkg.status }}</span>
                  </a>
                }
              </div>
              <a routerLink="/packages" class="mt-2 text-xs text-dm-blue hover:underline block">View all →</a>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class DashboardWarehouseComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);

  protected trucks: any[] = [];
  protected actionablePackages: any[] = [];
  protected packagedCount = 0;
  protected readyCount = 0;
  protected inTransitCount = 0;
  protected damagedCount = 0;
  protected loading = true;

  ngOnInit(): void {
    let pending = 2;
    const done = () => { if (--pending === 0) this.loading = false; };

    this.api.getPackages({ limit: 100 }).subscribe({
      next: (res) => {
        const items = res.items;
        this.packagedCount = items.filter((p: any) => p.status === 'packaged').length;
        this.readyCount = items.filter((p: any) => p.status === 'ready_for_shipping').length;
        this.inTransitCount = items.filter((p: any) => p.status === 'in_transit').length;
        this.damagedCount = items.filter((p: any) => p.status === 'damaged').length;
        this.actionablePackages = items.filter((p: any) =>
          p.status === 'packaged' || p.status === 'ready_for_shipping'
        );
        done();
      },
      error: () => done(),
    });

    this.api.getTrucks().subscribe({
      next: (trucks) => { this.trucks = trucks; done(); },
      error: () => done(),
    });
  }
}
