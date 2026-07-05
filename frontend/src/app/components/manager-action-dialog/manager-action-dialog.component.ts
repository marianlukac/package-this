import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

const ACTIONS = [
  { value: 'approve_reroute', label: 'Approve Reroute' },
  { value: 'override_priority', label: 'Override Priority' },
  { value: 'mark_customer_unhappy', label: 'Mark Customer Unhappy' },
  { value: 'approve_return', label: 'Approve Return' },
  { value: 'approve_expensive_delivery', label: 'Approve Expensive Delivery' },
  { value: 'force_truck_reassignment', label: 'Force Truck Reassignment' },
  { value: 'trigger_demo_scenario', label: 'Trigger Demo Scenario' },
];

@Component({
  selector: 'app-manager-action-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" role="dialog"
         aria-modal="true" aria-labelledby="manager-dialog-title" (keydown.escape)="close()">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-sm p-6 space-y-4" (click)="$event.stopPropagation()">
        <h2 id="manager-dialog-title" class="text-lg font-semibold text-gray-900">Manager Action</h2>

        <div>
          <label class="label" for="action-select">Action *</label>
          <select id="action-select" class="input" [(ngModel)]="selectedAction" autofocus>
            @for (a of actions; track a.value) {
              <option [value]="a.value">{{ a.label }}</option>
            }
          </select>
        </div>
        <div>
          <label class="label" for="action-reason">Reason *</label>
          <input id="action-reason" class="input" [(ngModel)]="reason" placeholder="Why is this action needed?" />
        </div>

        @if (selectedAction === 'override_priority') {
          <div>
            <label class="label" for="new-priority">New Priority</label>
            <select id="new-priority" class="input" [(ngModel)]="newPriority">
              <option value="standard">Standard</option>
              <option value="express">Express</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        }
        @if (selectedAction === 'force_truck_reassignment') {
          <div>
            <label class="label" for="new-truck">New Truck ID</label>
            <input id="new-truck" class="input" [(ngModel)]="newTruckId" placeholder="TRUCK-01" />
          </div>
        }
        @if (selectedAction === 'trigger_demo_scenario') {
          <div>
            <label class="label" for="scenario">Scenario Name</label>
            <select id="scenario" class="input" [(ngModel)]="scenarioName">
              <option value="delayed_delivery">Delayed Delivery</option>
              <option value="damaged_package">Damaged Package</option>
              <option value="reroute_required">Reroute Required</option>
              <option value="return_request">Return Request</option>
              <option value="complaint_escalation">Complaint Escalation</option>
            </select>
          </div>
        }

        @if (errorMsg) {
          <p class="text-xs text-red-600" role="alert">{{ errorMsg }}</p>
        }
        @if (successMsg) {
          <p class="text-xs text-green-600" role="status">{{ successMsg }}</p>
        }

        <div class="flex gap-2 justify-end">
          <button class="btn-secondary" (click)="close()">Cancel</button>
          <button class="btn-primary" [disabled]="!selectedAction || !reason || busy" (click)="submit()">
            Apply Action
          </button>
        </div>
      </div>
    </div>
  `,
})
export class ManagerActionDialogComponent {
  @Input({ required: true }) entityId!: string;
  @Input() entityType = 'package';
  @Output() closed = new EventEmitter<boolean>();

  protected actions = ACTIONS;
  private api = inject(ApiService);
  protected selectedAction = 'approve_reroute';
  protected reason = '';
  protected newPriority = 'urgent';
  protected newTruckId = '';
  protected scenarioName = 'delayed_delivery';
  protected busy = false;
  protected errorMsg = '';
  protected successMsg = '';

  submit(): void {
    this.busy = true;
    this.errorMsg = '';
    this.successMsg = '';

    const payload: Record<string, unknown> = {};
    if (this.selectedAction === 'override_priority') payload['priority'] = this.newPriority;
    if (this.selectedAction === 'force_truck_reassignment') payload['new_truck_id'] = this.newTruckId;
    if (this.selectedAction === 'trigger_demo_scenario') payload['scenario_name'] = this.scenarioName;

    this.api.performManagerAction(this.selectedAction, this.entityId, this.reason, payload).subscribe({
      next: () => {
        this.busy = false;
        this.successMsg = 'Action applied.';
        setTimeout(() => this.closed.emit(true), 800);
      },
      error: (err) => {
        this.busy = false;
        if (err.status === 403) {
          this.errorMsg = 'Manager persona required.';
        } else {
          this.errorMsg = err.error?.detail ?? 'Error performing action.';
        }
      },
    });
  }

  close(): void {
    this.closed.emit(false);
  }
}
