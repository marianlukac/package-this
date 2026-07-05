import { Component, OnInit, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-complaint-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card border-l-4 border-red-400 space-y-3">
      <h2 class="font-semibold text-gray-800">New Complaint</h2>

      <div>
        <label class="label" for="cmp-sale">Sale ID *</label>
        <input id="cmp-sale" class="input" [(ngModel)]="saleId" placeholder="SALE-2026-XXXXXXXX" />
      </div>
      <div>
        <label class="label" for="cmp-desc">Description *</label>
        <textarea id="cmp-desc" class="input" rows="3" [(ngModel)]="description"
                  placeholder="Describe the issue…"></textarea>
      </div>
      <div>
        <label class="label" for="cmp-pkgs">Package IDs (comma-separated)</label>
        <input id="cmp-pkgs" class="input" [(ngModel)]="packageIdsRaw"
               placeholder="PKG-2026-XXXXXXXX, PKG-2026-YYYYYYYY" />
      </div>

      @if (errorMsg) {
        <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
      }

      <div class="flex gap-2">
        <button class="btn-primary text-sm" [disabled]="!saleId || !description || busy" (click)="submit()">
          Submit Complaint
        </button>
        <button class="btn-secondary text-sm" (click)="cancelled.emit()">Cancel</button>
      </div>
    </div>
  `,
})
export class ComplaintCreateComponent {
  @Output() created = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  private api = inject(ApiService);
  protected saleId = '';
  protected description = '';
  protected packageIdsRaw = '';
  protected busy = false;
  protected errorMsg = '';

  submit(): void {
    this.busy = true;
    this.errorMsg = '';
    const packageIds = this.packageIdsRaw
      .split(',').map(s => s.trim()).filter(Boolean);

    this.api.createComplaint({ sale_id: this.saleId, description: this.description, package_ids: packageIds }).subscribe({
      next: () => { this.busy = false; this.created.emit(); },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error creating complaint.'; },
    });
  }
}
