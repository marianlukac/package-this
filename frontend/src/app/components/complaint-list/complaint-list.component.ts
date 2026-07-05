import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Complaint } from '../../models/complaint.model';
import { ComplaintCreateComponent } from '../complaint-create/complaint-create.component';

@Component({
  selector: 'app-complaint-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, ComplaintCreateComponent],
  template: `
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">Complaints</h1>
        <button class="btn-primary" (click)="showCreate = !showCreate">+ New Complaint</button>
      </div>

      @if (showCreate) {
        <app-complaint-create (created)="onCreated()" (cancelled)="showCreate = false" />
      }

      <!-- Filter -->
      <div class="flex gap-3 items-center">
        <select class="input w-36" [(ngModel)]="filterStatus" (change)="load()" aria-label="Filter by status">
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading…</p>
      } @else if (complaints.length === 0) {
        <div class="card text-center py-12 text-gray-400">No complaints found.</div>
      } @else {
        <div class="space-y-3">
          @for (c of complaints; track c.complaint_id) {
            <a [routerLink]="['/complaints', c.complaint_id]"
               class="card block hover:border-dm-blue transition-colors focus:ring-2 focus:ring-dm-blue"
               [attr.aria-label]="'View complaint ' + c.complaint_id">
              <div class="flex items-start justify-between">
                <div>
                  <span class="font-medium text-gray-900">{{ c.complaint_id }}</span>
                  <span class="text-xs text-gray-500 ml-2">Sale {{ c.sale_id }}</span>
                </div>
                <span [class]="c.status === 'open' ? 'badge bg-red-100 text-red-700' : 'badge bg-gray-100 text-gray-600'">
                  {{ c.status }}
                </span>
              </div>
              <p class="text-sm text-gray-700 mt-1 line-clamp-2">{{ c.description }}</p>
              <div class="text-xs text-gray-400 mt-1">
                {{ c.created_by_name }} · {{ c.created_at | date:'short' }}
                @if (c.package_ids.length > 0) {
                  · {{ c.package_ids.length }} package(s)
                }
              </div>
            </a>
          }
        </div>
      }
    </div>
  `,
})
export class ComplaintListComponent implements OnInit {
  private api = inject(ApiService);
  protected complaints: Complaint[] = [];
  protected loading = true;
  protected filterStatus = 'open';
  protected showCreate = false;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    const params: Record<string, string> = {};
    if (this.filterStatus) params['status'] = this.filterStatus;
    this.api.getComplaints(params).subscribe(res => {
      this.complaints = res;
      this.loading = false;
    });
  }

  onCreated(): void {
    this.showCreate = false;
    this.load();
  }
}
