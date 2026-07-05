import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Package, LineItem } from '../../models/package.model';

@Component({
  selector: 'app-line-item-manager',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <h2 class="font-semibold text-gray-800 mb-3">Line Items</h2>

      @if (package.line_items.length === 0) {
        <p class="text-xs text-gray-400">No line items yet.</p>
      } @else {
        <table class="w-full text-sm mb-3" role="grid" aria-label="Line items">
          <thead>
            <tr class="text-xs text-gray-500 border-b">
              <th scope="col" class="text-left pb-1">Product</th>
              <th scope="col" class="text-left pb-1">Category</th>
              <th scope="col" class="text-center pb-1">Qty</th>
              <th scope="col" class="text-left pb-1">Type</th>
              <th scope="col" class="text-left pb-1">Fragile</th>
              @if (!isTerminal) {
                <th scope="col" class="pb-1"></th>
              }
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            @for (item of package.line_items; track item.id) {
              <tr>
                <td class="py-1.5 text-gray-800">{{ item.product_name }}</td>
                <td class="py-1.5 text-gray-500">{{ item.product_category ?? '—' }}</td>
                <td class="py-1.5 text-center">{{ item.quantity }} {{ item.unit_description }}</td>
                <td class="py-1.5 text-gray-500 capitalize">{{ item.product_type.replace('_', ' ') }}</td>
                <td class="py-1.5">{{ item.fragile ? '🔺' : '—' }}</td>
                @if (!isTerminal) {
                  <td class="py-1.5">
                    <button class="text-xs text-red-500 hover:text-red-700 focus:underline"
                            [disabled]="package.line_items.length <= 1"
                            (click)="removeItem(item)"
                            [attr.aria-label]="'Remove ' + item.product_name">
                      Remove
                    </button>
                  </td>
                }
              </tr>
            }
          </tbody>
        </table>
      }

      @if (!isTerminal) {
        <details class="text-sm" #addForm>
          <summary class="cursor-pointer text-dm-blue hover:underline text-xs">+ Add Line Item</summary>
          <div class="mt-3 space-y-2 p-3 bg-gray-50 rounded-md">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="label text-xs" for="li-name">Product Name *</label>
                <input id="li-name" class="input text-xs" [(ngModel)]="newItem.product_name" placeholder="A4 White 80gsm" />
              </div>
              <div>
                <label class="label text-xs" for="li-cat">Category</label>
                <input id="li-cat" class="input text-xs" [(ngModel)]="newItem.product_category" placeholder="Paper" />
              </div>
              <div>
                <label class="label text-xs" for="li-qty">Quantity *</label>
                <input id="li-qty" type="number" class="input text-xs" [(ngModel)]="newItem.quantity" min="1" />
              </div>
              <div>
                <label class="label text-xs" for="li-unit">Unit</label>
                <input id="li-unit" class="input text-xs" [(ngModel)]="newItem.unit_description" placeholder="ream" />
              </div>
              <div>
                <label class="label text-xs" for="li-type">Type</label>
                <select id="li-type" class="input text-xs" [(ngModel)]="newItem.product_type">
                  <option value="paper">Paper</option>
                  <option value="office_supply">Office Supply</option>
                </select>
              </div>
              <div class="flex items-center gap-2 mt-4">
                <input type="checkbox" id="li-fragile" [(ngModel)]="newItem.fragile" class="rounded" />
                <label for="li-fragile" class="text-xs">Fragile</label>
              </div>
            </div>
            <div class="flex gap-2">
              <button class="btn-primary text-xs" [disabled]="!newItem.product_name || busy" (click)="addItem()">Add</button>
              <button class="btn-secondary text-xs" (click)="resetForm()">Cancel</button>
            </div>
            @if (errorMsg) {
              <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
            }
          </div>
        </details>
      }
    </div>
  `,
})
export class LineItemManagerComponent {
  @Input({ required: true }) package!: Package;
  @Input() isTerminal = false;
  @Output() changed = new EventEmitter<void>();

  private api = inject(ApiService);
  protected busy = false;
  protected errorMsg = '';
  protected newItem = this.emptyItem();

  private emptyItem() {
    return { product_name: '', product_category: '', quantity: 1, unit_description: 'unit', product_type: 'paper', fragile: false };
  }

  addItem(): void {
    this.busy = true;
    this.errorMsg = '';
    this.api.addLineItem(this.package.package_id, this.newItem).subscribe({
      next: () => { this.busy = false; this.resetForm(); this.changed.emit(); },
      error: (err) => { this.busy = false; this.errorMsg = err.error?.detail ?? 'Error adding item.'; },
    });
  }

  removeItem(item: LineItem): void {
    if (!confirm(`Remove "${item.product_name}"?`)) return;
    this.api.removeLineItem(this.package.package_id, item.id).subscribe({
      next: () => this.changed.emit(),
      error: (err) => alert(err.error?.detail ?? 'Cannot remove item.'),
    });
  }

  resetForm(): void {
    this.newItem = this.emptyItem();
    this.errorMsg = '';
  }
}
