import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';
import { StatusCardsComponent } from '../status-cards/status-cards.component';
import { EventStreamComponent } from '../event-stream/event-stream.component';
import { DemoControlsComponent } from '../demo-controls/demo-controls.component';
import { DashboardSalesComponent } from '../dashboard-sales/dashboard-sales.component';
import { DashboardAccountingComponent } from '../dashboard-accounting/dashboard-accounting.component';
import { DashboardWarehouseComponent } from '../dashboard-warehouse/dashboard-warehouse.component';
import { DashboardManagerComponent } from '../dashboard-manager/dashboard-manager.component';
import { OperationalSummary } from '../../models/sale.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, RouterLink,
    StatusCardsComponent, EventStreamComponent, DemoControlsComponent,
    DashboardSalesComponent, DashboardAccountingComponent,
    DashboardWarehouseComponent, DashboardManagerComponent,
  ],
  template: `
    <div class="space-y-6">
      @switch (roleGroup) {
        @case ('manager') {
          <app-dashboard-manager />
          @if (summary) {
            <app-status-cards [summary]="summary" />
          }
          <app-event-stream [maxItems]="8" />
          <app-demo-controls (reset)="loadSummary()" />
        }
        @case ('sales') {
          <app-dashboard-sales />
          @if (summary) {
            <app-status-cards [summary]="summary" />
          }
        }
        @case ('accounting') {
          <app-dashboard-accounting />
          @if (summary) {
            <app-status-cards [summary]="summary" />
          }
        }
        @case ('warehouse') {
          <app-dashboard-warehouse />
          @if (summary) {
            <app-status-cards [summary]="summary" />
          }
        }
        @default {
          <!-- General view for reception, QA, temp roles -->
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Operations Dashboard</h1>
              <p class="text-sm text-gray-500 mt-1">
                {{ persona.currentPersonaProfile()?.name }} — Scranton Branch
              </p>
            </div>
            <a routerLink="/sales/new" class="btn-primary">+ New Sale</a>
          </div>

          @if (summary) {
            <app-status-cards [summary]="summary" />
          }

          <div class="card">
            <h2 class="font-semibold text-gray-800 mb-3">Recent Packages</h2>
            @if (loading) {
              <p class="text-sm text-gray-400">Loading...</p>
            } @else if (recentPackages.length === 0) {
              <p class="text-sm text-gray-400">No packages found. Create a sale to get started.</p>
            } @else {
              <div class="space-y-2">
                @for (pkg of recentPackages; track pkg.package_id) {
                  <a [routerLink]="['/packages', pkg.package_id]"
                     class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:border-dm-blue hover:bg-blue-50 transition-colors cursor-pointer">
                    <div>
                      <span class="text-sm font-medium text-gray-900">{{ pkg.package_id }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ pkg.customer_name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      @if (pkg.delay_reason) {
                        <span class="badge bg-orange-100 text-orange-700" title="Delayed">⚠ Delayed</span>
                      }
                      <span [class]="'status-' + pkg.status">{{ pkg.status }}</span>
                    </div>
                  </a>
                }
              </div>
              <a routerLink="/packages" class="mt-3 text-xs text-dm-blue hover:underline block">View all packages →</a>
            }
          </div>

          <app-event-stream [maxItems]="8" />
        }
      }
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  protected api = inject(ApiService);
  protected persona = inject(PersonaService);
  protected summary: OperationalSummary | null = null;
  protected recentPackages: any[] = [];
  protected loading = true;

  get roleGroup(): string {
    return this.persona.getRoleGroup();
  }

  ngOnInit(): void {
    this.loadSummary();
  }

  loadSummary(): void {
    this.loading = true;
    this.api.getOperationalSummary().subscribe(s => this.summary = s);
    this.api.getPackages({ limit: 10 }).subscribe(res => {
      this.recentPackages = res.items;
      this.loading = false;
    });
  }
}
