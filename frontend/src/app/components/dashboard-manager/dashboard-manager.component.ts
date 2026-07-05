import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';

interface ManagerSummary {
  at_risk: number;
  delayed: number;
  backorder_count: number;
  order_created_count: number;
  open_complaints: number;
  damaged: number;
  returned: number;
  active_trucks: number;
  customer_unhappy_count: number;
  // computed playful
  kevin_reroutes: number;
  most_dramatic_pkg: string;
  dwight_escalations: number;
  attention_score: number;
}

@Component({
  selector: 'app-dashboard-manager',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Manager Dashboard</h1>
          <p class="text-sm text-gray-500 mt-1">Regional Manager — Scranton Branch</p>
        </div>
        <a routerLink="/sales/new" class="btn-primary">+ New Sale</a>
      </div>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading operations data...</p>
      } @else {
        <!-- Serious Metrics -->
        <section aria-label="Operational metrics">
          <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Operational Metrics</h2>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <a routerLink="/packages" [queryParams]="{}" class="card text-center hover:border-red-400 transition-colors focus:ring-2 focus:ring-red-400">
              <div class="text-2xl font-bold" [class.text-red-600]="summary.at_risk > 0" [class.text-gray-400]="summary.at_risk === 0">{{ summary.at_risk }}</div>
              <div class="text-xs text-gray-500 mt-1">At Risk</div>
            </a>
            <a routerLink="/packages" class="card text-center hover:border-orange-400 transition-colors focus:ring-2 focus:ring-orange-400">
              <div class="text-2xl font-bold" [class.text-orange-600]="summary.delayed > 0" [class.text-gray-400]="summary.delayed === 0">{{ summary.delayed }}</div>
              <div class="text-xs text-gray-500 mt-1">Delayed</div>
            </a>
            <a routerLink="/packages" [queryParams]="{status: 'backorder'}" class="card text-center hover:border-yellow-400 transition-colors focus:ring-2 focus:ring-yellow-400">
              <div class="text-2xl font-bold text-yellow-600">{{ summary.backorder_count }}</div>
              <div class="text-xs text-gray-500 mt-1">Backorders</div>
            </a>
            <a routerLink="/complaints" class="card text-center hover:border-red-400 transition-colors focus:ring-2 focus:ring-red-400">
              <div class="text-2xl font-bold" [class.text-red-600]="summary.open_complaints > 0" [class.text-gray-400]="summary.open_complaints === 0">{{ summary.open_complaints }}</div>
              <div class="text-xs text-gray-500 mt-1">Open Complaints</div>
            </a>
            <a routerLink="/packages" [queryParams]="{status: 'damaged'}" class="card text-center hover:border-gray-400 transition-colors">
              <div class="text-2xl font-bold text-gray-600">{{ summary.damaged }}</div>
              <div class="text-xs text-gray-500 mt-1">Damaged</div>
            </a>
            <a routerLink="/packages" [queryParams]="{status: 'returned'}" class="card text-center hover:border-gray-400 transition-colors">
              <div class="text-2xl font-bold text-gray-600">{{ summary.returned }}</div>
              <div class="text-xs text-gray-500 mt-1">Returned</div>
            </a>
            <a routerLink="/map" class="card text-center hover:border-purple-400 transition-colors focus:ring-2 focus:ring-purple-400">
              <div class="text-2xl font-bold text-purple-600">{{ summary.active_trucks }}</div>
              <div class="text-xs text-gray-500 mt-1">Trucks Active</div>
            </a>
            <div class="card text-center">
              <div class="text-2xl font-bold" [class.text-red-600]="summary.customer_unhappy_count > 0" [class.text-gray-400]="summary.customer_unhappy_count === 0">{{ summary.customer_unhappy_count }}</div>
              <div class="text-xs text-gray-500 mt-1">Unhappy Customers</div>
            </div>
          </div>
        </section>

        <!-- Playful Metrics -->
        <section aria-label="Dunder Mifflin metrics">
          <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            🏆 Dunder Mifflin Branch Intelligence
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div class="card border border-yellow-200 bg-yellow-50">
              <div class="text-xs font-semibold text-yellow-700 mb-1">🍔 Kevin-Related Reroutes</div>
              <div class="text-2xl font-bold text-yellow-800">{{ summary.kevin_reroutes }}</div>
              <div class="text-xs text-gray-500 mt-1">Packages delayed by Kevin's culinary priorities</div>
              @if (summary.kevin_reroutes === 0) {
                <div class="text-xs text-yellow-600 mt-1 italic">Kevin has been suspiciously responsible lately.</div>
              }
            </div>

            <div class="card border border-blue-200 bg-blue-50">
              <div class="text-xs font-semibold text-blue-700 mb-1">🎭 Most Dramatic Incident</div>
              <div class="text-base font-bold text-blue-800 truncate">{{ summary.most_dramatic_pkg || 'None yet' }}</div>
              <div class="text-xs text-gray-500 mt-1">Package with most activity in the system</div>
            </div>

            <div class="card border border-gray-200 bg-gray-50">
              <div class="text-xs font-semibold text-gray-700 mb-1">🥋 Dwight Escalation Count</div>
              <div class="text-2xl font-bold text-gray-800">{{ summary.dwight_escalations }}</div>
              <div class="text-xs text-gray-500 mt-1">High-priority complaints raised by Dwight</div>
              @if (summary.dwight_escalations > 0) {
                <div class="text-xs text-red-600 mt-1 italic">Bears. Beets. Battlestar Galactica.</div>
              }
            </div>

            <div class="card border border-amber-200 bg-amber-50">
              <div class="text-xs font-semibold text-amber-700 mb-1">🥨 Pretzel Day Truck Status</div>
              <div class="text-sm font-bold text-amber-800">All clear — no pretzel emergency</div>
              <div class="text-xs text-gray-500 mt-1">Trucks are on legitimate routes today</div>
            </div>

            <div class="card border border-purple-200 bg-purple-50">
              <div class="text-xs font-semibold text-purple-700 mb-1">📊 Regional Manager Attention Score</div>
              <div class="text-2xl font-bold text-purple-800">{{ summary.attention_score }}</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ attentionLabel(summary.attention_score) }}
              </div>
            </div>

            <div class="card border border-red-200 bg-red-50">
              <div class="text-xs font-semibold text-red-700 mb-1">😤 Customer Unhappiness Warning</div>
              <div class="text-2xl font-bold text-red-800">{{ summary.customer_unhappy_count }}</div>
              <div class="text-xs text-gray-500 mt-1">Customers currently marked as unhappy</div>
              @if (summary.customer_unhappy_count === 0) {
                <div class="text-xs text-green-600 mt-1 italic">That's what she said — about good service!</div>
              }
            </div>
          </div>
        </section>
      }
    </div>
  `,
})
export class DashboardManagerComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);

  protected loading = true;
  protected summary: ManagerSummary = {
    at_risk: 0, delayed: 0, backorder_count: 0, order_created_count: 0,
    open_complaints: 0, damaged: 0, returned: 0, active_trucks: 0,
    customer_unhappy_count: 0, kevin_reroutes: 0, most_dramatic_pkg: '',
    dwight_escalations: 0, attention_score: 0,
  };

  ngOnInit(): void {
    let pending = 4;
    const done = () => { if (--pending === 0) this.loading = false; };

    this.api.getOperationalSummary().subscribe({
      next: (s: any) => {
        this.summary.delayed = s.delayed ?? 0;
        this.summary.open_complaints = s.open_complaints ?? 0;
        this.summary.active_trucks = s.active_trucks ?? 0;
        this.summary.backorder_count = s.backorder_count ?? 0;
        this.summary.order_created_count = s.order_created_count ?? 0;
        this.summary.customer_unhappy_count = s.customer_unhappy_count ?? 0;
        done();
      },
      error: () => done(),
    });

    this.api.getAtRiskPackages().subscribe({
      next: (pkgs: any[]) => {
        this.summary.at_risk = pkgs.length;
        done();
      },
      error: () => done(),
    });

    this.api.getPackages({ limit: 100 }).subscribe({
      next: (res: any) => {
        const items = res.items;
        this.summary.damaged = items.filter((p: any) => p.status === 'damaged').length;
        this.summary.returned = items.filter((p: any) => p.status === 'returned').length;

        // Kevin-related reroutes: salesperson = kevin-malone AND delay_reason contains "hungry"
        this.summary.kevin_reroutes = items.filter((p: any) =>
          p.salesperson_id === 'kevin-malone' && p.delay_reason &&
          p.delay_reason.toLowerCase().includes('hungry')
        ).length;

        // Most dramatic: find the package with delay + complaints (proxy for "most activity")
        const delayed = items.filter((p: any) => p.delay_reason);
        if (delayed.length > 0) {
          this.summary.most_dramatic_pkg = delayed[0].package_id;
        } else if (items.length > 0) {
          this.summary.most_dramatic_pkg = items[0].package_id;
        }

        this.summary.attention_score = this.summary.open_complaints + this.summary.delayed + this.summary.at_risk;
        done();
      },
      error: () => done(),
    });

    this.api.getComplaints().subscribe({
      next: (complaints: any[]) => {
        // Dwight escalation count: complaints by dwight-schrute
        this.summary.dwight_escalations = complaints.filter((c: any) =>
          c.created_by_id === 'dwight-schrute' && c.status === 'open'
        ).length;
        done();
      },
      error: () => done(),
    });
  }

  attentionLabel(score: number): string {
    if (score === 0) return 'Operations running smoothly — Michael approves.';
    if (score <= 3) return 'Manageable. Nothing World\'s Best Boss can\'t handle.';
    if (score <= 7) return 'Getting spicy. Michael may need to make an announcement.';
    return 'DEFCON MICHAEL. Emergency improv performance imminent.';
  }
}
