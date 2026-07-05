import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-sale-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="max-w-xl mx-auto space-y-5">
      <div>
        <a routerLink="/dashboard" class="text-xs text-dm-blue hover:underline">← Dashboard</a>
        <h1 class="text-2xl font-bold text-gray-900 mt-1">New Sale</h1>
      </div>

      <div class="card space-y-4">
        <div>
          <label class="label" for="sale-customer">Customer *</label>
          <select id="sale-customer" class="input" [(ngModel)]="customerId">
            <option value="">Select a customer…</option>
            @for (c of customers; track c.customer_id) {
              <option [value]="c.customer_id">{{ c.name }}</option>
            }
          </select>
        </div>
        <div>
          <label class="label" for="sale-notes">Notes</label>
          <textarea id="sale-notes" class="input" rows="3" [(ngModel)]="notes"
                    placeholder="Optional order notes"></textarea>
        </div>

        @if (errorMsg) {
          <p class="text-sm text-red-600" role="alert">{{ errorMsg }}</p>
        }

        <div class="flex gap-2">
          <button class="btn-primary" [disabled]="!customerId || busy" (click)="submit()">Create Sale</button>
          <a routerLink="/dashboard" class="btn-secondary">Cancel</a>
        </div>
      </div>

      @if (createdSaleId) {
        <div class="card bg-green-50 border-green-200">
          <p class="text-sm text-green-800">
            Sale <strong>{{ createdSaleId }}</strong> created!
            <a [routerLink]="['/packages']" [queryParams]="{sale_id: createdSaleId}"
               class="underline ml-1">Add packages →</a>
          </p>
        </div>
      }
    </div>
  `,
})
export class SaleCreateComponent implements OnInit {
  private api = inject(ApiService);
  private router = inject(Router);
  protected customers: any[] = [];
  protected customerId = '';
  protected notes = '';
  protected busy = false;
  protected errorMsg = '';
  protected createdSaleId = '';

  ngOnInit(): void {
    this.api.getCustomers().subscribe(c => this.customers = c);
  }

  submit(): void {
    this.busy = true;
    this.errorMsg = '';
    this.api.createSale({ customer_id: this.customerId, notes: this.notes }).subscribe({
      next: (sale) => {
        this.busy = false;
        this.createdSaleId = sale.sale_id;
      },
      error: (err) => {
        this.busy = false;
        this.errorMsg = err.error?.detail ?? 'Error creating sale.';
      },
    });
  }
}
