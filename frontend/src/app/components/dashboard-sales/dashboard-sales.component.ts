import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';

@Component({
  selector: 'app-dashboard-sales',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">My Sales Dashboard</h1>
          <p class="text-sm text-gray-500 mt-1">
            {{ persona.currentPersonaProfile()?.name }} — {{ persona.currentPersonaProfile()?.role }}
          </p>
        </div>
        <a routerLink="/sales/new" class="btn-primary">+ New Sale</a>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card text-center">
          <div class="text-2xl font-bold text-dm-blue">{{ myPackages.length }}</div>
          <div class="text-xs text-gray-500 mt-1">My Packages</div>
        </div>
        <div class="card text-center">
          <div class="text-2xl font-bold" [class.text-orange-600]="myDelayed.length > 0" [class.text-gray-400]="myDelayed.length === 0">
            {{ myDelayed.length }}
          </div>
          <div class="text-xs text-gray-500 mt-1">Delayed</div>
        </div>
        <div class="card text-center">
          <div class="text-2xl font-bold" [class.text-red-600]="openComplaints > 0" [class.text-gray-400]="openComplaints === 0">
            {{ openComplaints }}
          </div>
          <div class="text-xs text-gray-500 mt-1">Open Complaints</div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- My Packages -->
        <div class="card">
          <h2 class="font-semibold text-gray-800 mb-3">My Packages</h2>
          @if (loading) {
            <p class="text-sm text-gray-400">Loading...</p>
          } @else if (myPackages.length === 0) {
            <p class="text-sm text-gray-400">No packages for your sales yet — create a sale to get started.</p>
          } @else {
            <div class="space-y-1.5">
              @for (pkg of myPackages.slice(0, 8); track pkg.package_id) {
                <a [routerLink]="['/packages', pkg.package_id]"
                   class="flex items-center justify-between p-2 rounded border border-gray-100 hover:border-dm-blue hover:bg-blue-50 transition-colors text-sm">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-dm-blue text-xs">{{ pkg.package_id }}</span>
                    <span class="text-gray-600 text-xs font-semibold">{{ pkg.customer_name }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    @if (pkg.delay_reason) {
                      <span class="badge bg-orange-100 text-orange-700 text-xs">⚠ Delayed</span>
                    }
                    <span [class]="'status-' + pkg.status" class="text-xs">{{ pkg.status }}</span>
                  </div>
                </a>
              }
            </div>
            <a routerLink="/packages" [queryParams]="{salesperson_id: persona.currentPersonaId()}"
               class="mt-2 text-xs text-dm-blue hover:underline block">View all my packages →</a>
          }
        </div>

        <!-- Delays affecting my sales -->
        <div class="card">
          <h2 class="font-semibold text-gray-800 mb-3">Delays Affecting My Sales</h2>
          @if (myDelayed.length === 0) {
            <p class="text-sm text-gray-400">No delays on your packages. Nice work!</p>
          } @else {
            <div class="space-y-1.5">
              @for (pkg of myDelayed; track pkg.package_id) {
                <a [routerLink]="['/packages', pkg.package_id]"
                   class="flex items-center justify-between p-2 rounded border border-orange-100 bg-orange-50 hover:border-orange-400 transition-colors text-sm">
                  <span class="font-medium text-xs text-dm-blue">{{ pkg.package_id }}</span>
                  <span class="text-xs text-orange-700 truncate ml-2">{{ pkg.delay_reason }}</span>
                </a>
              }
            </div>
          }

          <div class="mt-4 border-t border-gray-100 pt-3">
            <h3 class="text-xs font-semibold text-gray-600 mb-2">Open Complaints on My Sales</h3>
            @if (complaints.length === 0) {
              <p class="text-xs text-gray-400">No open complaints.</p>
            } @else {
              <div class="space-y-1">
                @for (c of complaints.slice(0, 4); track c.complaint_id) {
                  <a [routerLink]="['/complaints', c.complaint_id]"
                     class="flex items-center justify-between p-1.5 rounded text-xs hover:bg-red-50 transition-colors">
                    <span class="text-red-700 font-medium">{{ c.complaint_id }}</span>
                    <span class="text-gray-500 truncate ml-2">{{ c.description }}</span>
                  </a>
                }
              </div>
              <a routerLink="/complaints" class="mt-1 text-xs text-dm-blue hover:underline block">View all →</a>
            }
          </div>
        </div>
      </div>
    </div>
  `,
})
export class DashboardSalesComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);

  protected myPackages: any[] = [];
  protected myDelayed: any[] = [];
  protected complaints: any[] = [];
  protected openComplaints = 0;
  protected loading = true;

  ngOnInit(): void {
    const personaId = this.persona.currentPersonaId();

    this.api.getPackages({ salesperson_id: personaId, limit: 50 }).subscribe(res => {
      this.myPackages = res.items;
      this.myDelayed = res.items.filter((p: any) => p.delay_reason);
      this.loading = false;
    });

    this.api.getComplaints({ salesperson_id: personaId }).subscribe(complaints => {
      this.complaints = complaints.filter((c: any) => c.status === 'open');
      this.openComplaints = this.complaints.length;
    });
  }
}
