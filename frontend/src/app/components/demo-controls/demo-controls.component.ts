import { Component, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

interface Scenario {
  name: string;
  label: string;
  description: string;
}

const SCENARIOS: Scenario[] = [
  {
    name: 'delayed-delivery',
    label: 'Delayed Delivery',
    description: 'A package gets stuck in transit with a delay reason.',
  },
  {
    name: 'damaged-in-transit',
    label: 'Damaged in Transit',
    description: 'A package is marked damaged en route to the customer.',
  },
  {
    name: 'kevin-hunger-reroute',
    label: "Kevin's Hunger Reroute",
    description: 'Kevin redirects the truck for a snack detour, causing a delay.',
  },
  {
    name: 'complaint-and-return',
    label: 'Complaint Escalation',
    description: 'An angry customer creates a complaint on an in-transit package.',
  },
  {
    name: 'manager-reroute',
    label: 'Return Request',
    description: 'A package is rerouted by manager approval with priority bump.',
  },
];

@Component({
  selector: 'app-demo-controls',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card border-l-4 border-dm-gold" role="region" aria-label="Demo controls">
      <h2 class="font-semibold text-gray-800 mb-3 text-sm">🎬 Demo Controls</h2>

      <div class="space-y-3">
        <!-- Reset -->
        <div>
          @if (!confirmReset) {
            <button
              class="btn-secondary w-full text-xs justify-center"
              [disabled]="busy"
              (click)="confirmReset = true"
              aria-label="Reset all demo data to baseline"
            >
              🔄 Reset to Baseline
            </button>
          } @else {
            <div class="flex gap-2">
              <button
                class="flex-1 text-xs px-3 py-1.5 rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                [disabled]="busy"
                (click)="doReset()"
              >
                @if (busy && activeScenario === '__reset__') {
                  <span class="animate-spin mr-1">⏳</span>
                }
                Confirm Reset
              </button>
              <button
                class="text-xs px-3 py-1.5 rounded border border-gray-300 hover:bg-gray-50"
                (click)="confirmReset = false"
              >Cancel</button>
            </div>
          }
        </div>

        <!-- Scenarios -->
        <div class="border-t border-gray-100 pt-2">
          <p class="text-xs text-gray-500 mb-2 font-medium">Run Scenario</p>
          <div class="space-y-1.5">
            @for (s of scenarios; track s.name) {
              <button
                class="w-full text-left text-xs px-2 py-2 rounded border border-transparent hover:border-dm-blue hover:bg-blue-50 transition-colors focus:outline-none focus:ring-1 focus:ring-dm-blue disabled:opacity-40 disabled:cursor-not-allowed"
                [disabled]="busy"
                (click)="runScenario(s)"
                [attr.aria-label]="'Run scenario: ' + s.label"
              >
                <div class="font-medium text-gray-800 flex items-center gap-1.5">
                  @if (busy && activeScenario === s.name) {
                    <span class="animate-spin text-sm">⏳</span>
                  }
                  {{ s.label }}
                </div>
                <div class="text-gray-400 mt-0.5">{{ s.description }}</div>
              </button>
            }
          </div>
        </div>
      </div>

      <!-- Result summary panel (FR-026 success feedback) -->
      @if (resultSummary) {
        <div class="mt-3 p-2 rounded border text-xs"
             [class.border-green-200]="!error"
             [class.bg-green-50]="!error"
             [class.text-green-800]="!error"
             [class.border-red-200]="error"
             [class.bg-red-50]="error"
             [class.text-red-800]="error"
             role="status"
             aria-live="polite">
          {{ resultSummary }}
        </div>
      }
    </div>
  `,
})
export class DemoControlsComponent {
  @Output() reset = new EventEmitter<void>();

  protected scenarios = SCENARIOS;
  private api = inject(ApiService);
  protected busy = false;
  protected confirmReset = false;
  protected activeScenario = '';
  protected resultSummary = '';
  protected error = false;

  doReset(): void {
    this.busy = true;
    this.activeScenario = '__reset__';
    this.resultSummary = '';
    this.api.resetDemo().subscribe({
      next: (res) => {
        this.busy = false;
        this.confirmReset = false;
        this.activeScenario = '';
        const count = res?.seeded_packages ?? '?';
        this.resultSummary = `✅ Reset complete — ${count} packages restored to baseline seed state.`;
        this.error = false;
        this.reset.emit();
      },
      error: (err) => {
        this.busy = false;
        this.confirmReset = false;
        this.activeScenario = '';
        this.resultSummary = err.error?.detail ?? 'Reset failed. Please try again.';
        this.error = true;
      },
    });
  }

  runScenario(scenario: Scenario): void {
    this.busy = true;
    this.activeScenario = scenario.name;
    this.resultSummary = '';
    this.error = false;

    this.api.runScenario(scenario.name).subscribe({
      next: (res) => {
        this.busy = false;
        this.activeScenario = '';
        const affected = res?.affected_packages;
        if (affected && affected.length > 0) {
          this.resultSummary = `✅ "${scenario.label}" complete — affected: ${affected.join(', ')}.`;
        } else {
          this.resultSummary = `✅ "${scenario.label}" executed successfully.`;
        }
        this.error = false;
        this.reset.emit();
      },
      error: (err) => {
        this.busy = false;
        this.activeScenario = '';
        this.resultSummary = err.error?.detail ?? `Scenario "${scenario.label}" failed.`;
        this.error = true;
      },
    });
  }
}
