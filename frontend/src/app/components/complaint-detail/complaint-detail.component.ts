import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { PersonaService } from '../../services/persona.service';
import { Complaint } from '../../models/complaint.model';

@Component({
  selector: 'app-complaint-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="max-w-2xl space-y-4">
      <a routerLink="/complaints" class="text-xs text-dm-blue hover:underline">← All Complaints</a>

      @if (loading) {
        <p class="text-sm text-gray-400">Loading…</p>
      } @else if (!complaint) {
        <div class="card text-center py-12 text-gray-400">Complaint not found.</div>
      } @else {
        <div class="card space-y-3">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-xl font-bold">{{ complaint.complaint_id }}</h1>
              <p class="text-sm text-gray-500">Sale {{ complaint.sale_id }} · {{ complaint.created_by_name }}</p>
            </div>
            <span [class]="complaint.status === 'open' ? 'badge bg-red-100 text-red-700' : 'badge bg-gray-100 text-gray-600'">
              {{ complaint.status }}
            </span>
          </div>

          <p class="text-sm text-gray-800">{{ complaint.description }}</p>

          @if (complaint.package_ids.length > 0) {
            <div>
              <p class="text-xs font-medium text-gray-500 mb-1">Related Packages</p>
              <div class="flex flex-wrap gap-1">
                @for (pid of complaint.package_ids; track pid) {
                  <a [routerLink]="['/packages', pid]"
                     class="badge bg-blue-50 text-dm-blue hover:underline">{{ pid }}</a>
                }
              </div>
            </div>
          }

          <div class="text-xs text-gray-400">
            Created {{ complaint.created_at | date:'medium' }}
            @if (complaint.closed_at) { · Closed {{ complaint.closed_at | date:'medium' }} }
          </div>
        </div>

        @if (complaint.status === 'open') {
          <div class="card space-y-3">
            <h2 class="font-semibold text-gray-800">Update Complaint</h2>
            <div>
              <label class="label" for="upd-desc">Description</label>
              <textarea id="upd-desc" class="input" rows="3" [(ngModel)]="updatedDescription">{{ complaint.description }}</textarea>
            </div>
            <div class="flex gap-2">
              <button class="btn-primary text-sm" [disabled]="busy" (click)="update()">Update</button>
              <button class="btn-danger text-sm" [disabled]="busy" (click)="close()">Close Complaint</button>
            </div>
            @if (errorMsg) {
              <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
            }
          </div>
        }
      }
    </div>
  `,
})
export class ComplaintDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);
  protected persona = inject(PersonaService);
  protected complaint: Complaint | null = null;
  protected loading = true;
  protected updatedDescription = '';
  protected busy = false;
  protected errorMsg = '';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    this.api.getComplaint(id).subscribe({
      next: (c) => { this.complaint = c; this.updatedDescription = c.description; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  update(): void {
    if (!this.complaint) return;
    this.busy = true;
    this.api.updateComplaint(this.complaint.complaint_id, this.updatedDescription).subscribe({
      next: (c) => { this.complaint = c; this.busy = false; },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error updating.'; },
    });
  }

  close(): void {
    if (!this.complaint || !confirm('Close this complaint?')) return;
    this.busy = true;
    this.api.closeComplaint(this.complaint.complaint_id).subscribe({
      next: (c) => { this.complaint = c; this.busy = false; },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error closing.'; },
    });
  }
}
