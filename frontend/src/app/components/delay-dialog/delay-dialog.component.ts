import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-delay-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" role="dialog"
         aria-modal="true" aria-labelledby="delay-dialog-title" (keydown.escape)="close()">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-sm p-6 space-y-4" (click)="$event.stopPropagation()">
        <h2 id="delay-dialog-title" class="text-lg font-semibold text-gray-900">Record Delay</h2>

        <div>
          <label class="label" for="delay-reason">Delay Reason *</label>
          <input id="delay-reason" class="input" [(ngModel)]="reason" placeholder="Truck breakdown, weather, etc."
                 autofocus />
        </div>
        <div>
          <label class="label" for="delay-hours">Estimated Duration (hours) *</label>
          <input id="delay-hours" type="number" class="input" [(ngModel)]="hours" min="0.5" step="0.5" />
        </div>

        @if (errorMsg) {
          <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
        }

        <div class="flex gap-2 justify-end">
          <button class="btn-secondary" (click)="close()">Cancel</button>
          <button class="btn-warning" [disabled]="!reason || !hours || busy" (click)="submit()">Record Delay</button>
        </div>
      </div>
    </div>
  `,
})
export class DelayDialogComponent {
  @Input({ required: true }) packageId!: string;
  @Output() closed = new EventEmitter<boolean>();

  private api = inject(ApiService);
  protected reason = '';
  protected hours = 2;
  protected busy = false;
  protected errorMsg = '';

  submit(): void {
    this.busy = true;
    this.errorMsg = '';
    this.api.recordDelay(this.packageId, this.reason, this.hours).subscribe({
      next: () => { this.busy = false; this.closed.emit(true); },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error recording delay.'; },
    });
  }

  close(): void {
    this.closed.emit(false);
  }
}
