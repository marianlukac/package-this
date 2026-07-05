import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';

const TERMINAL_STATUSES = ['delivered', 'returned', 'damaged', 'cancelled'];

@Component({
  selector: 'app-dashboard-accounting',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-5">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Accounting Dashboard</h1>
        <p class="text-sm text-gray-500 mt-1">
          {{ persona.currentPersonaProfile()?.name }} — {{ persona.currentPersonaProfile()?.role }}
        </p>
      </div>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading...</p>
      } @else {
        <!-- Summary cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="card text-center">
            <div class="text-2xl font-bold text-dm-blue">{{ totalInvoices }}</div>
            <div class="text-xs text-gray-500 mt-1">Total Invoices</div>
          </div>
          <div class="card text-center">
            <div class="text-2xl font-bold" [class.text-red-600]="returnedCount > 0" [class.text-gray-400]="returnedCount === 0">
              {{ returnedCount }}
            </div>
            <div class="text-xs text-gray-500 mt-1">Returned</div>
          </div>
          <div class="card text-center">
            <div class="text-2xl font-bold" [class.text-orange-600]="damagedCount > 0" [class.text-gray-400]="damagedCount === 0">
              {{ damagedCount }}
            </div>
            <div class="text-xs text-gray-500 mt-1">Damaged</div>
          </div>
          <div class="card text-center">
            <div class="text-2xl font-bold" [class.text-gray-600]="cancelledCount > 0" [class.text-gray-400]="cancelledCount === 0">
              {{ cancelledCount }}
            </div>
            <div class="text-xs text-gray-500 mt-1">Cancelled</div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <!-- Financial Exception Packages -->
          <div class="card">
            <h2 class="font-semibold text-gray-800 mb-3">Financial Exception Packages</h2>
            @if (exceptionPackages.length === 0) {
              <p class="text-sm text-gray-400">All invoices clear — no exception packages.</p>
            } @else {
              <div class="space-y-1.5">
                @for (pkg of exceptionPackages.slice(0, 10); track pkg.package_id) {
                  <a [routerLink]="['/packages', pkg.package_id]"
                     class="flex items-center justify-between p-2 rounded border border-gray-100 hover:border-dm-blue hover:bg-blue-50 transition-colors text-sm">
                    <div>
                      <span class="font-medium text-dm-blue text-xs">{{ pkg.package_id }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ pkg.customer_name }}</span>
                    </div>
                    <span [class]="'status-' + pkg.status" class="text-xs">{{ pkg.status }}</span>
                  </a>
                }
              </div>
              <a routerLink="/packages" class="mt-2 text-xs text-dm-blue hover:underline block">View all exceptions →</a>
            }
          </div>

          <!-- Recent Sales Activity -->
          <div class="card">
            <h2 class="font-semibold text-gray-800 mb-3">Recent Invoice Activity</h2>
            @if (recentSales.length === 0) {
              <p class="text-sm text-gray-400">No recent sales.</p>
            } @else {
              <div class="space-y-1.5">
                @for (sale of recentSales.slice(0, 8); track sale.sale_id) {
                  <div class="flex items-center justify-between p-2 rounded border border-gray-100 text-sm">
                    <div>
                      <span class="font-medium text-xs text-dm-blue">{{ sale.sale_id }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ sale.customer_id }}</span>
                    </div>
                    <span class="text-xs text-gray-400">{{ sale.created_at | date:'shortDate' }}</span>
                  </div>
                }
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class DashboardAccountingComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);

  protected exceptionPackages: any[] = [];
  protected recentSales: any[] = [];
  protected totalInvoices = 0;
  protected returnedCount = 0;
  protected damagedCount = 0;
  protected cancelledCount = 0;
  protected loading = true;

  ngOnInit(): void {
    Promise.all([
      this.loadPackages(),
      this.loadSales(),
    ]).then(() => { this.loading = false; });
  }

  private loadPackages(): Promise<void> {
    return new Promise(resolve => {
      this.api.getPackages({ exception_state: 'any', limit: 100 }).subscribe({
        next: (res) => {
          const exceptions = res.items.filter((p: any) => TERMINAL_STATUSES.includes(p.status));
          this.exceptionPackages = exceptions;
          this.returnedCount = exceptions.filter((p: any) => p.status === 'returned').length;
          this.damagedCount = exceptions.filter((p: any) => p.status === 'damaged').length;
          this.cancelledCount = exceptions.filter((p: any) => p.status === 'cancelled').length;
          resolve();
        },
        error: () => resolve(),
      });
    });
  }

  private loadSales(): Promise<void> {
    return new Promise(resolve => {
      this.api.getSales().subscribe({
        next: (res) => {
          const items = Array.isArray(res) ? res : (res.items ?? []);
          this.recentSales = items;
          this.totalInvoices = items.length;
          resolve();
        },
        error: () => resolve(),
      });
    });
  }
}
