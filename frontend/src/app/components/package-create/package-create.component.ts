import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Package } from '../../models/package.model';

@Component({
  selector: 'app-package-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card border-l-4 border-dm-blue space-y-3">
      <h2 class="font-semibold text-gray-800">Add Package to Sale {{ saleId }}</h2>

      <div class="grid grid-cols-2 gap-3">
        <div class="col-span-2">
          <label class="label" for="pkg-destination">Destination *</label>
          <input id="pkg-destination" class="input" [(ngModel)]="form.destination"
                 placeholder="123 Office Park, Scranton PA" />
        </div>
        <div>
          <label class="label" for="pkg-priority">Priority</label>
          <select id="pkg-priority" class="input" [(ngModel)]="form.priority">
            <option value="standard">Standard</option>
            <option value="express">Express</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div class="flex items-center gap-2 mt-5">
          <input type="checkbox" id="pkg-fragile" [(ngModel)]="form.fragile" class="rounded" />
          <label for="pkg-fragile" class="text-sm">Fragile</label>
        </div>
        <div class="col-span-2">
          <label class="label" for="pkg-contents">Contents Summary</label>
          <input id="pkg-contents" class="input" [(ngModel)]="form.contents_summary"
                 placeholder="e.g. 500 reams A4, 3 boxes staples" />
        </div>
      </div>

      @if (errorMsg) {
        <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
      }

      <div class="flex gap-2">
        <button class="btn-primary text-sm" [disabled]="!form.destination || busy" (click)="submit()">
          Add Package
        </button>
        <button class="btn-secondary text-sm" (click)="cancelled.emit()">Cancel</button>
      </div>
    </div>
  `,
})
export class PackageCreateComponent {
  @Input({ required: true }) saleId!: string;
  @Output() created = new EventEmitter<Package>();
  @Output() cancelled = new EventEmitter<void>();

  private api = inject(ApiService);
  protected form = {
    destination: '',
    priority: 'standard',
    contents_summary: '',
    fragile: false,
  };
  protected busy = false;
  protected errorMsg = '';

  submit(): void {
    this.busy = true;
    this.errorMsg = '';
    this.api.createPackage({ sale_id: this.saleId, ...this.form }).subscribe({
      next: (pkg) => { this.busy = false; this.created.emit(pkg); },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error creating package.'; },
    });
  }
}
